const $ = (id) => document.getElementById(id);

const INTERVALO_ESTADO_MS = 3000;

let dbAnterior = null;

function mostrarEstado(dbOk, texto, cacheEstado) {
  $("estado-db").className = "punto " + (dbOk ? "ok" : "caido");
  $("estado-texto").textContent = texto;
  const clase = cacheEstado === "ok" ? "ok" : cacheEstado === "caida" ? "caido" : "desconocido";
  const etiqueta = cacheEstado === "ok" ? "conectada" : cacheEstado === "caida" ? "caída" : "no aplica";
  $("estado-cache").className = "punto " + clase;
  $("estado-cache-texto").textContent = "Caché: " + etiqueta;
}

async function actualizarEstado() {
  try {
    const respuesta = await fetch("/status", { cache: "no-store" });
    const datos = await respuesta.json();
    const dbOk = datos.db === "ok";
    mostrarEstado(dbOk, dbOk ? "BD conectada" : "BD caída", datos.cache);
    if (dbOk && dbAnterior === false) recuperar();
    dbAnterior = dbOk;
  } catch {
    mostrarEstado(false, "Sin conexión con la web", "desconocido");
    dbAnterior = false;
  }
}

actualizarEstado();
setInterval(actualizarEstado, INTERVALO_ESTADO_MS);

let runActual = null;

function mostrarMensaje(texto) {
  $("mensaje").textContent = texto;
}

async function pedirConCabeceras(url, opciones) {
  const respuesta = await fetch(url, opciones);
  if (respuesta.status >= 500) {
    throw new Error("El servidor no puede acceder a la base de datos ahora mismo. Inténtalo de nuevo.");
  }
  const cuerpo = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    const detalle = cuerpo && cuerpo.detail;
    throw new Error(
      typeof detalle === "string" ? detalle : Array.isArray(detalle) ? detalle[0].msg : "Solicitud no válida"
    );
  }
  return { cuerpo, cabeceras: respuesta.headers };
}

async function pedir(url, opciones) {
  return (await pedirConCabeceras(url, opciones)).cuerpo;
}

function enviarJSON(datos) {
  return {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  };
}

function elemento(etiqueta, texto, clase) {
  const nodo = document.createElement(etiqueta);
  if (texto !== undefined) nodo.textContent = texto;
  if (clase) nodo.className = clase;
  return nodo;
}

// ---------- Figuras de Pokémon (pixel art) ----------
// Los dibujos llegan ya recortados (make sprites-*). Para que el pixel art se vea nítido se amplía por un
// número ENTERO de píxeles reales de pantalla (teniendo en cuenta el zoom de Windows) y sin suavizado.
// Todas usan la misma escala, así se respetan los tamaños relativos como en los juegos.
function figura(speciesId, gris, tam, reduccion = 1) {
  const caja = elemento("div", undefined, "figura" + (gris ? " gris" : ""));
  caja.style.width = caja.style.height = tam * reduccion + "px";
  if (!speciesId) {
    caja.append(elemento("span", "?", "falta"));
    return caja;
  }
  const img = new Image();
  img.onerror = () => caja.replaceChildren(elemento("span", "?", "falta"));
  img.onload = () => {
    const dpr = window.devicePixelRatio || 1;
    const lado = Math.max(img.naturalWidth, img.naturalHeight);
    let k = Math.max(1, Math.round((tam * dpr) / 56));
    while (k > 1 && lado * k > tam * dpr * 1.35) k--;
    const lienzo = Math.max(Math.round(tam * dpr), lado * k);
    const cv = document.createElement("canvas");
    cv.width = cv.height = lienzo;
    const css = (lienzo / dpr) * reduccion;
    cv.style.width = cv.style.height = css + "px";
    if (reduccion !== 1) cv.style.imageRendering = "pixelated";
    if (css > tam * reduccion) cv.style.margin = `${(tam * reduccion - css) / 2}px`;
    const cx = cv.getContext("2d");
    cx.imageSmoothingEnabled = false;
    const dw = img.naturalWidth * k, dh = img.naturalHeight * k;
    cx.drawImage(img, Math.floor((lienzo - dw) / 2), Math.floor((lienzo - dh) / 2), dw, dh);
    caja.replaceChildren(cv);
  };
  img.src = `/sprites/${speciesId}.png`;
  return caja;
}

// ---------- Navegación por la dirección: #/ (portada) y #/partida/<id> ----------
function rutaActual() {
  const partida = location.hash.match(/^#\/partida\/(\d+)$/);
  return partida ? { vista: "partida", id: Number(partida[1]) } : { vista: "inicio" };
}

function mostrarVista(nombre) {
  $("vista-inicio").hidden = nombre !== "inicio";
  $("vista-partida").hidden = nombre !== "partida";
}

// Aviso que debe sobrevivir a un cambio de vista (por ejemplo, al volver a la portada desde una partida inexistente)
let avisoPendiente = "";

async function navegar() {
  mostrarMensaje(avisoPendiente);
  avisoPendiente = "";
  const ruta = rutaActual();
  try {
    if (ruta.vista === "partida") await abrirPartida(ruta.id);
    else await mostrarInicio();
  } catch (error) {
    mostrarMensaje(error.message);
  }
}

window.addEventListener("hashchange", navegar);

// ---------- Portada ----------
async function mostrarInicio() {
  runActual = null;
  const runs = await pedir("/runs");
  const tarjetas = runs.map((run) => {
    const tarjeta = elemento("button", undefined, "partida");
    tarjeta.type = "button";
    tarjeta.append(
      elemento("h3", run.name),
      elemento("div", `${run.alive} vivos · ${run.dead} muertos`, "meta")
    );
    const minis = elemento("div", undefined, "minis");
    if (run.party.length) {
      for (const p of run.party) minis.append(figura(p.species_id, !p.alive, 56, 0.8));
    } else {
      minis.append(elemento("span", "Aún sin equipo", "vacio"));
    }
    tarjeta.append(minis);
    tarjeta.addEventListener("click", () => { location.hash = `#/partida/${run.id}`; });
    return tarjeta;
  });

  const nueva = elemento("button", undefined, "partida nueva");
  nueva.type = "button";
  const contenido = elemento("span");
  contenido.append(elemento("span", "+", "mas"), elemento("span", "Nueva partida"));
  nueva.append(contenido);
  nueva.addEventListener("click", () => {
    $("nombre-run").value = "";
    $("dialogo-nueva").showModal();
  });

  $("rejilla").replaceChildren(...tarjetas, nueva);
  mostrarVista("inicio");
}

// ---------- Partida ----------
async function abrirPartida(id) {
  const runs = await pedir("/runs");
  const run = runs.find((r) => r.id === id);
  if (!run) {
    avisoPendiente = "Esa partida no existe.";
    location.hash = "#/";
    return;
  }
  runActual = id;
  $("titulo-partida").textContent = run.name;
  mostrarVista("partida");
  await cargarRun();
}

function recuperar() {
  navegar();
}

function mostrarInfoCache(cabeceras) {
  const estado = cabeceras.get("X-Cache");
  const ttl = cabeceras.get("X-Cache-TTL");
  const ms = cabeceras.get("X-Latency-Ms");
  const origen = estado === "HIT" ? "caché" : "base de datos";
  let texto = `Origen: ${origen} · ${ms} ms`;
  if (ttl !== null) texto += ` · caduca en ${ttl} s`;
  if (estado === "DEGRADED") texto += " · caché caída";
  $("info-cache").textContent = texto;
}

async function cargarRun() {
  if (!runActual) return;

  const [equipo, eventos, muertos] = await Promise.all([
    pedirConCabeceras(`/runs/${runActual}/team`),
    pedir(`/runs/${runActual}/encounters`),
    pedir(`/runs/${runActual}/graveyard`),
  ]);

  const vivos = equipo.cuerpo;
  mostrarInfoCache(equipo.cabeceras);

  $("vivos").replaceChildren(...vivos.map((p) => elemento("li", `${p.species} (${p.route})`)));
  $("cementerio").replaceChildren(...muertos.map((p) => elemento("li", `${p.species} (${p.route})`)));

  const porRuta = new Map();
  for (const e of eventos) {
    if (e.event_type === "muerte") {
      if (porRuta.has(e.route)) porRuta.get(e.route).muerto = true;
      continue;
    }
    porRuta.set(e.route, { resultado: e.event_type, especie: e.species, muerto: false });
  }
  $("rutas").replaceChildren(
    ...[...porRuta].map(([ruta, fila]) => {
      const tr = document.createElement("tr");
      tr.append(
        elemento("td", ruta),
        elemento("td", fila.resultado + (fila.muerto ? " (muerto)" : "")),
        elemento("td", fila.especie)
      );
      return tr;
    })
  );
}

$("form-run").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  mostrarMensaje("");
  try {
    const run = await pedir("/runs", enviarJSON({ name: $("nombre-run").value }));
    $("dialogo-nueva").close();
    location.hash = `#/partida/${run.id}`;
  } catch (error) {
    $("dialogo-nueva").close();
    mostrarMensaje(error.message);
  }
});

$("cancelar-nueva").addEventListener("click", () => $("dialogo-nueva").close());

const RETARDO_SUGERENCIAS_MS = 200;

let temporizadorSugerencias = null;
let peticionSugerencias = 0;

async function cargarSugerencias() {
  const texto = $("especie").value.trim();
  const numero = ++peticionSugerencias;
  if (!texto) {
    $("lista-especies").replaceChildren();
    return;
  }
  try {
    const nombres = await pedir(`/species?q=${encodeURIComponent(texto)}`);
    if (numero !== peticionSugerencias) return;
    $("lista-especies").replaceChildren(...nombres.map((nombre) => new Option(nombre)));
  } catch {
    // las sugerencias son opcionales: si fallan, no se molesta al usuario
  }
}

$("especie").addEventListener("input", () => {
  clearTimeout(temporizadorSugerencias);
  temporizadorSugerencias = setTimeout(cargarSugerencias, RETARDO_SUGERENCIAS_MS);
});

$("form-evento").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  mostrarMensaje("");
  try {
    await pedir(
      `/runs/${runActual}/events`,
      enviarJSON({ event_type: $("tipo-evento").value, route: $("ruta").value, species: $("especie").value })
    );
    $("ruta").value = "";
    $("especie").value = "";
    await cargarRun();
  } catch (error) {
    mostrarMensaje(error.message);
  }
});

navegar();
