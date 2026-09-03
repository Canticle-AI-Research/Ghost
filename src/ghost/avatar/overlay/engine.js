/**
 * Ghost desktop overlay: a camera-facing 2D ghost-bunny in Three.js.
 * Desktop windows and folders are targeting data, not holograms.
 */
const FACE_GLYPHS = {
  awake: "❯ █",
  done: "❯ █",
  happy: "^ ^",
  blissful: "‿ ‿",
  wink: "^ █",
  excited: "✧ ✧",
  focused: "▪ ▪",
  blank: "・ ・",
  curious: "? ・",
  surprised: "o o",
  sleepy: "⌒ ⌒",
  error: "x x",
  confused: "@ @",
  angry: "▼ ▼",
  nervous: "; ;",
};

const RGB_STOPS = [
  0xf7768e, 0xff9e64, 0xe0af68, 0x9ece6a, 0x7dcfff, 0x7aa2f7, 0xe478d0,
];

let scene, camera, renderer, avatarGroup, bunnySprite;
let wsClient = null;
let currentFace = "awake";
let rimHex = RGB_STOPS[0];
let isStealth = false;
let isInside = false;
let isBusy = false;
let agentState = "idle";
let desktopWindows = [];
let desktopItems = [];
let lastEnterScreen = null;
let idleTimer = 0;

function init() {
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 2000);
  camera.position.set(0, 0, 600);

  renderer = new THREE.WebGLRenderer({
    canvas: document.getElementById("stage"),
    alpha: true,
    antialias: true,
  });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setClearColor(0x000000, 0);

  avatarGroup = new THREE.Group();
  bunnySprite = makeBunnySprite();
  avatarGroup.add(bunnySprite);
  scene.add(avatarGroup);

  const rest = screenToWorld(window.innerWidth * 0.72, window.innerHeight * 0.38, 0);
  avatarGroup.position.copy(rest);

  setupRaycasting();
  setupWebSocket();
  setFace("awake");
  animateSpawn();
  animate();

  window.addEventListener("resize", onWindowResize);
}

function makeBunnySprite() {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const texture = new THREE.CanvasTexture(canvas);
  texture.minFilter = THREE.LinearFilter;
  const material = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
    depthTest: false,
  });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(160, 160, 1);
  sprite.userData.canvas = canvas;
  sprite.userData.texture = texture;
  return sprite;
}

function hexToRgb(hex) {
  return {
    r: (hex >> 16) & 255,
    g: (hex >> 8) & 255,
    b: hex & 255,
  };
}

function drawBunny() {
  const canvas = bunnySprite.userData.canvas;
  const ctx = canvas.getContext("2d");
  const { r, g, b } = hexToRgb(rimHex);
  ctx.clearRect(0, 0, 256, 256);

  ctx.save();
  ctx.translate(128, 140);
  ctx.fillStyle = `rgba(${Math.min(255, r + 80)}, ${Math.min(255, g + 40)}, ${Math.min(255, b + 60)}, 0.22)`;
  ctx.strokeStyle = `rgb(${r}, ${g}, ${b})`;
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.ellipse(0, 8, 78, 88, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(-18, -78);
  ctx.bezierCurveTo(-8, -118, 28, -124, 22, -82);
  ctx.stroke();

  ctx.beginPath();
  ctx.ellipse(-72, 18, 14, 10, -0.4, 0, Math.PI * 2);
  ctx.ellipse(72, 18, 14, 10, 0.4, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  ctx.restore();

  const glyph = FACE_GLYPHS[currentFace] || FACE_GLYPHS.blank;
  ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
  ctx.font = "bold 42px 'Fira Code', 'JetBrains Mono', monospace";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.shadowColor = `rgba(${r}, ${g}, ${b}, 0.8)`;
  ctx.shadowBlur = 12;
  ctx.fillText(glyph, 128, 148);
  ctx.shadowBlur = 0;

  bunnySprite.userData.texture.needsUpdate = true;
}

function setFace(face) {
  if (!FACE_GLYPHS[face]) return;
  currentFace = face;
  drawBunny();
}

function screenToWorld(sx, sy, z = 0) {
  const ndcX = (sx / window.innerWidth) * 2 - 1;
  const ndcY = -(sy / window.innerHeight) * 2 + 1;
  const vec = new THREE.Vector3(ndcX, ndcY, 0.5);
  vec.unproject(camera);
  const dir = vec.sub(camera.position).normalize();
  const distance = (z - camera.position.z) / dir.z;
  return camera.position.clone().add(dir.multiplyScalar(distance));
}

function worldToScreen(pos) {
  const projected = pos.clone().project(camera);
  return {
    x: (projected.x * 0.5 + 0.5) * window.innerWidth,
    y: (-projected.y * 0.5 + 0.5) * window.innerHeight,
  };
}

function restScreen() {
  const spots = [
    [0.22, 0.42],
    [0.72, 0.32],
    [0.55, 0.58],
    [0.38, 0.68],
  ];
  const pick = spots[Math.floor(Math.random() * spots.length)];
  return { x: window.innerWidth * pick[0], y: window.innerHeight * pick[1] };
}

function findWindow(kind, name) {
  const needle = (name || "").toLowerCase();
  if (kind === "browser") {
    return desktopWindows.find((w) =>
      /chrome|chromium|firefox|brave|navigator/i.test(`${w.wm_class} ${w.title}`)
    ) || desktopWindows.find((w) => (w.title || "").toLowerCase().includes(needle));
  }
  if (needle) {
    return desktopWindows.find((w) => (w.title || "").toLowerCase().includes(needle));
  }
  return null;
}

function findItem(name) {
  const needle = (name || "").toLowerCase();
  return desktopItems.find((item) => (item.name || "").toLowerCase().includes(needle));
}

function targetScreen(kind, name) {
  if (kind === "item") {
    const item = findItem(name);
    if (item) return { x: item.x + 40, y: item.y + 40, item };
  }
  const win = findWindow(kind, name);
  if (win) {
    return {
      x: win.x + win.width / 2,
      y: win.y + win.height / 2,
      window: win,
    };
  }
  if (kind === "browser") {
    return { x: window.innerWidth * 0.5, y: window.innerHeight * 0.45 };
  }
  return null;
}

function tweenTo(worldPos, duration, onComplete) {
  isBusy = true;
  new TWEEN.Tween(avatarGroup.position)
    .to({ x: worldPos.x, y: worldPos.y, z: worldPos.z }, duration)
    .easing(TWEEN.Easing.Cubic.Out)
    .onComplete(() => {
      isBusy = false;
      if (onComplete) onComplete();
    })
    .start();
}

function enterTarget(kind, name) {
  const target = targetScreen(kind, name);
  if (!target) {
    setFace("confused");
    showSpeech("I can't find that on the desktop.");
    return;
  }
  lastEnterScreen = { x: target.x, y: target.y };
  setFace("focused");
  const world = screenToWorld(target.x, target.y, 0);
  tweenTo(world, 700, () => {
    if (target.item && wsClient && wsClient.readyState === WebSocket.OPEN) {
      wsClient.send(JSON.stringify({ type: "open_item", path: target.item.path }));
    }
    isBusy = true;
    new TWEEN.Tween(avatarGroup.scale)
      .to({ x: 0.18, y: 0.18, z: 0.18 }, 380)
      .easing(TWEEN.Easing.Cubic.In)
      .onComplete(() => {
        isInside = true;
        isBusy = false;
        avatarGroup.visible = false;
        const status = document.getElementById("agent-status");
        if (status) status.textContent = "Ghost: Inside";
      })
      .start();
  });
}

function popOut(face) {
  const spot = restScreen();
  const world = screenToWorld(spot.x, spot.y, 0);
  avatarGroup.visible = true;
  avatarGroup.scale.set(0.2, 0.2, 0.2);
  if (lastEnterScreen) {
    avatarGroup.position.copy(screenToWorld(lastEnterScreen.x, lastEnterScreen.y, 0));
  }
  setFace(face || "done");
  isInside = false;
  isBusy = true;
  tweenTo(world, 650, () => {
    new TWEEN.Tween(avatarGroup.scale)
      .to({ x: 1, y: 1, z: 1 }, 400)
      .easing(TWEEN.Easing.Back.Out)
      .onComplete(() => {
        isBusy = false;
        const status = document.getElementById("agent-status");
        if (status) status.textContent = "Ghost: Idle";
      })
      .start();
  });
}

function toggleStealthMode() {
  isStealth = !isStealth;
  const statusElem = document.getElementById("agent-status");
  if (isStealth) {
    setFace("sleepy");
    isInside = false;
    avatarGroup.visible = true;
    new TWEEN.Tween(avatarGroup.scale)
      .to({ x: 0.28, y: 0.28, z: 0.28 }, 400)
      .start();
    const corner = screenToWorld(window.innerWidth - 70, window.innerHeight - 70, 0);
    tweenTo(corner, 500);
    if (statusElem) statusElem.textContent = "Ghost: Stealth";
  } else {
    setFace("awake");
    new TWEEN.Tween(avatarGroup.scale)
      .to({ x: 1, y: 1, z: 1 }, 400)
      .start();
    const rest = screenToWorld(window.innerWidth * 0.72, window.innerHeight * 0.38, 0);
    tweenTo(rest, 500);
    if (statusElem) statusElem.textContent = "Ghost: Active";
  }
}

function showSpeech(text, duration = 2800) {
  const bubble = document.getElementById("speech-bubble");
  const speechText = document.getElementById("speech-text");
  if (!bubble || !speechText) return;
  speechText.textContent = text;
  bubble.classList.remove("hidden");
  updateUIAnchors();
  clearTimeout(bubble._timer);
  bubble._timer = setTimeout(() => bubble.classList.add("hidden"), duration);
}

function updateUIAnchors() {
  if (!avatarGroup) return;
  const screenPos = worldToScreen(avatarGroup.position);
  const bubble = document.getElementById("speech-bubble");
  if (bubble) {
    bubble.style.left = `${screenPos.x}px`;
    bubble.style.top = `${screenPos.y - 20}px`;
  }
}

function animateSpawn() {
  avatarGroup.scale.set(0.01, 0.01, 0.01);
  setFace("awake");
  new TWEEN.Tween(avatarGroup.scale)
    .to({ x: 1, y: 1, z: 1 }, 700)
    .easing(TWEEN.Easing.Back.Out)
    .start();
}

function setupRaycasting() {
  window.addEventListener("click", (e) => {
    if (e.target.closest("#ui-container")) return;
    const mouse = new THREE.Vector2(
      (e.clientX / window.innerWidth) * 2 - 1,
      -(e.clientY / window.innerHeight) * 2 + 1
    );
    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObject(bunnySprite, false);
    if (hits.length > 0) {
      setFace("wink");
      showSpeech("here.");
      setTimeout(() => {
        if (currentFace === "wink") setFace("blank");
      }, 900);
    }
  });
}

function setupWebSocket() {
  const statusElem = document.getElementById("agent-status");
  const wsUrl = "ws://127.0.0.1:8765";

  function connect() {
    wsClient = new WebSocket(wsUrl);
    wsClient.onopen = () => {
      if (statusElem) statusElem.textContent = "Ghost: Connected";
    };
    wsClient.onmessage = (event) => {
      try {
        handleAgentMessage(JSON.parse(event.data));
      } catch (err) {
        console.error("WS parse error", err);
      }
    };
    wsClient.onclose = () => {
      if (statusElem) statusElem.textContent = "Ghost: Disconnected";
      setTimeout(connect, 2000);
    };
  }
  connect();
}

function handleAgentMessage(msg) {
  if (msg.type === "desktop_sync" && msg.state) {
    desktopWindows = msg.state.windows || [];
    desktopItems = msg.state.items || [];
    return;
  }
  if (msg.type === "agent_state") {
    agentState = msg.state || "idle";
    const statusElem = document.getElementById("agent-status");
    if (statusElem) statusElem.textContent = `Ghost: ${agentState}`;
    if (agentState === "thinking" && !isInside) setFace("focused");
    if (agentState === "error") setFace("error");
    return;
  }
  if (msg.type !== "avatar_action") return;

  if (msg.face) setFace(msg.face);
  if (msg.text) showSpeech(msg.text);

  if (msg.action === "enter") {
    enterTarget(msg.target_kind, msg.target_name);
  } else if (msg.action === "pop_out") {
    popOut(msg.face || "done");
  } else if (msg.action === "hide") {
    if (!isStealth) toggleStealthMode();
  } else if (msg.action === "appear") {
    if (isStealth) toggleStealthMode();
    else setFace(msg.face || "awake");
  } else if (msg.action === "idle" && !isInside && !isBusy && agentState === "idle") {
    const spot = restScreen();
    tweenTo(screenToWorld(spot.x, spot.y, 0), 900);
  } else if (msg.action === "touch" && msg.target_name) {
    enterTarget("item", msg.target_name);
  }
}

function triggerAction(actionName) {
  if (actionName === "stealth") {
    toggleStealthMode();
  } else if (actionName === "simulate_search") {
    agentState = "thinking";
    enterTarget("browser", "browser");
  } else if (actionName === "simulate_open") {
    const first = desktopItems[0];
    if (first) enterTarget("item", first.name);
    else showSpeech("No desktop folders found.");
  } else if (actionName === "finish") {
    popOut("done");
    agentState = "idle";
  }
}

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

let lastRimDraw = 0;
function cycleRim(time) {
  if (time - lastRimDraw < 80) return;
  lastRimDraw = time;
  const period = 8000;
  const t = (time % period) / period;
  const scaled = t * RGB_STOPS.length;
  const i = Math.floor(scaled) % RGB_STOPS.length;
  const j = (i + 1) % RGB_STOPS.length;
  const f = scaled - Math.floor(scaled);
  const a = hexToRgb(RGB_STOPS[i]);
  const b = hexToRgb(RGB_STOPS[j]);
  const mixed = {
    r: Math.round(a.r + (b.r - a.r) * f),
    g: Math.round(a.g + (b.g - a.g) * f),
    b: Math.round(a.b + (b.b - a.b) * f),
  };
  rimHex = (mixed.r << 16) | (mixed.g << 8) | mixed.b;
  drawBunny();
}

function maybeIdle(dt) {
  if (isInside || isBusy || isStealth || agentState !== "idle") {
    idleTimer = 0;
    return;
  }
  idleTimer += dt;
  if (idleTimer < 10000) return;
  idleTimer = 0;
  const faces = ["blank", "curious", "sleepy", "wink"];
  setFace(faces[Math.floor(Math.random() * faces.length)]);
  const spot = restScreen();
  tweenTo(screenToWorld(spot.x, spot.y, 0), 1000);
}

let lastTime = performance.now();
function animate(time) {
  requestAnimationFrame(animate);
  const dt = time - lastTime;
  lastTime = time;
  TWEEN.update(time);
  if (!isStealth && !isInside && avatarGroup) {
    avatarGroup.position.y += Math.sin(time * 0.0025) * 0.12;
  }
  cycleRim(time);
  maybeIdle(dt);
  updateUIAnchors();
  renderer.render(scene, camera);
}

function toggleBackground() {
  document.body.classList.toggle("transparent-mode");
}

window.triggerAction = triggerAction;

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("stealth-toggle")?.addEventListener("click", toggleStealthMode);
  document.getElementById("bg-toggle")?.addEventListener("click", toggleBackground);
  document.querySelectorAll("[data-action]").forEach((btn) => {
    btn.addEventListener("click", () => triggerAction(btn.dataset.action));
  });
  init();
});
