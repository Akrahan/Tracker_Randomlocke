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

function elemento(etiqueta, texto) {
  const nodo = document.createElement(etiqueta);
  nodo.textContent = texto;
  return nodo;
}

async function cargarRuns(seleccionar) {
  const runs = await pedir("/runs");
  const selector = $("selector-run");
  selector.replaceChildren(...runs.map((r) => new Option(r.name, r.id)));
  if (seleccionar) selector.value = seleccionar;
  await cargarRun();
}

function recuperar() {
  mostrarMensaje("");
  cargarRuns(runActual).catch((error) => mostrarMensaje(error.message));
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
  runActual = $("selector-run").value || null;
  $("seccion-eventos").hidden = !runActual;
  $("seccion-datos").hidden = !runActual;
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

$("selector-run").addEventListener("change", () => cargarRun().catch((e) => mostrarMensaje(e.message)));

$("form-run").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  mostrarMensaje("");
  try {
    const run = await pedir("/runs", enviarJSON({ name: $("nombre-run").value }));
    $("nombre-run").value = "";
    await cargarRuns(run.id);
  } catch (error) {
    mostrarMensaje(error.message);
  }
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

cargarRuns().catch((error) => mostrarMensaje(error.message));
