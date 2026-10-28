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
// Dos modos:
//  - suelta (portada y equipo): todas con la misma escala, así se respetan los tamaños relativos como en los juegos;
//  - encajada (listas, dentro de un cuadro blanco): cada una al mayor factor entero que quepa en su cuadro.
function figura(speciesId, gris, tam, reduccion = 1, encajada = false) {
  const caja = elemento("div", undefined, "figura" + (encajada ? " cuadro" : "") + (gris ? " gris" : ""));
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
    if (encajada) tam -= 4; // el cuadro tiene 2 px de borde por cada lado
    let k;
    if (encajada) {
      k = Math.floor((tam * 0.9 * dpr) / lado);
    } else {
      k = Math.max(1, Math.round((tam * dpr) / 56));
      while (k > 1 && lado * k > tam * dpr * 1.35) k--;
    }
    const suavizar = k < 1; // un dibujo grande que no cabe ni a tamaño real se reduce (aquí sí con suavizado)
    if (suavizar) k = (tam * 0.9 * dpr) / lado;
    const lienzo = encajada ? Math.round(tam * dpr) : Math.max(Math.round(tam * dpr), Math.ceil(lado * k));
    const cv = document.createElement("canvas");
    cv.width = cv.height = lienzo;
    const css = (lienzo / dpr) * reduccion;
    cv.style.width = cv.style.height = css + "px";
    if (reduccion !== 1) cv.style.imageRendering = "pixelated";
    if (css > tam * reduccion) cv.style.margin = `${(tam * reduccion - css) / 2}px`;
    const cx = cv.getContext("2d");
    cx.imageSmoothingEnabled = suavizar;
    const dw = Math.round(img.naturalWidth * k), dh = Math.round(img.naturalHeight * k);
    cx.drawImage(img, Math.floor((lienzo - dw) / 2), Math.floor((lienzo - dh) / 2), dw, dh);
    caja.replaceChildren(cv);
  };
  img.src = `/sprites/${speciesId}.png`;
  return caja;
}

// Miniatura de tamaño fijo (portada): el lado más largo de TODOS los dibujos mide lo mismo, así se ven
// todos por igual (un Pichu igual de visible que un Onix). Como el factor casi nunca es entero, se escala con
// «vecino más próximo» (pixelated): el pixel art sigue nítido, aunque algún píxel pueda salir algo más fino.
function miniatura(speciesId, gris, lado) {
  const caja = elemento("div", undefined, "figura" + (gris ? " gris" : ""));
  caja.style.width = caja.style.height = lado + "px";
  if (!speciesId) {
    caja.append(elemento("span", "?", "falta"));
    return caja;
  }
  const img = new Image();
  img.onerror = () => caja.replaceChildren(elemento("span", "?", "falta"));
  img.onload = () => {
    const f = lado / Math.max(img.naturalWidth, img.naturalHeight);
    img.width = Math.round(img.naturalWidth * f);
    img.height = Math.round(img.naturalHeight * f);
    img.style.imageRendering = "pixelated";
    caja.replaceChildren(img);
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
const TAMANO_MINIATURA = 44; // px: lado más largo de cada Pokémon en las tarjetas
async function mostrarInicio() {
  runActual = null;
  const runs = await pedir("/runs");
  const tarjetas = runs.map((run) => {
    const tarjeta = elemento("button", undefined, "partida");
    tarjeta.type = "button";
    tarjeta.append(
      elemento("span", NOMBRE_MODO[run.mode], "modo"),
      elemento("h3", run.name),
      elemento("div", `${run.alive} vivos · ${run.dead} muertos`, "meta")
    );
    const minis = elemento("div", undefined, "minis");
    if (run.party.length) {
      for (const p of run.party) minis.append(miniatura(p.species_id, !p.alive, TAMANO_MINIATURA));
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
  nueva.addEventListener("click", abrirNuevaPartida);

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
  $("modo-partida").textContent = NOMBRE_MODO[run.mode];
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

function contador(nombre, valor, clase) {
  const chip = elemento("span", nombre + " ", "chip" + (clase ? " " + clase : ""));
  chip.append(elemento("b", String(valor)));
  return chip;
}

// Fila de vivos o cementerio: mote (o «Sin mote»), especie y ruta; a la derecha, el dibujo en su cuadro blanco.
// Todo el texto va con textContent (vía elemento()), nunca como HTML: protege frente a XSS con motes como «<img onerror=...>».
function pintarLista(lista, pokemons, muertos, textoVacio) {
  const filas = pokemons.map((p) => {
    const fila = elemento("button", undefined, "fila");
    fila.type = "button";
    fila.addEventListener("click", () => abrirFicha(p, !muertos));
    const texto = elemento("div", undefined, "texto");
    texto.append(
      elemento("div", p.nickname || "Sin mote", "mote"),
      elemento("div", p.species, "esp"),
      elemento("div", p.route, "ruta")
    );
    fila.append(texto, figura(p.species_id, muertos, 64, 1, true));
    const li = elemento("li");
    li.append(fila);
    return li;
  });
  if (!filas.length) filas.push(elemento("li", textoVacio, "vacio"));
  lista.replaceChildren(...filas);
}

function pintarFallos(fallos) {
  const filas = fallos.map((e) => {
    const fila = elemento("li", undefined, "fila fallo");
    const texto = elemento("div", undefined, "texto");
    texto.append(elemento("div", e.species, "esp"), elemento("div", e.route, "ruta"));
    const borrar = elemento("button", "✕", "borrar");
    borrar.type = "button";
    borrar.title = "Eliminar este fallo";
    borrar.setAttribute("aria-label", `Eliminar el fallo de ${e.route}`);
    borrar.addEventListener("click", () => eliminarEncuentro(e.route, `el fallo de ${e.route} (${e.species})`));
    fila.append(texto, borrar);
    return fila;
  });
  if (!filas.length) filas.push(elemento("li", "Ningún fallo.", "vacio"));
  $("fallos").replaceChildren(...filas);
}

// ---------- Equipo (Pokédex) ----------
const TAMANO_EQUIPO = 6;
let equipoActual = [];  // lo que devuelve GET /party: posición, ruta, especie, mote, alive, species_id
let vivosActual = [];   // lo que devuelve GET /team: todos los vivos (equipo y PC)

// El equipo se guarda entero con PUT /party (una lista de rutas, máximo 6); la API valida
// y la base de datos garantiza que no haya más de 6 ni repetidos.
async function guardarEquipo(rutas) {
  mostrarMensaje("");
  try {
    await pedir(`/runs/${runActual}/party`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ routes: rutas }),
    });
  } catch (error) {
    mostrarMensaje(error.message);
  }
  await cargarRun();
}

function pintarEquipo() {
  const casillas = equipoActual.map((p) => {
    // La casilla no es un <button> porque dentro lleva otro botón (el «−»); se hace accesible con role y tabindex.
    const casilla = elemento("div", undefined, "slot" + (p.alive ? "" : " muerto"));
    casilla.tabIndex = 0;
    casilla.setAttribute("role", "button");
    casilla.setAttribute("aria-label", `${p.nickname || p.species}, ${p.route}`);

    const quitar = elemento("button", "−", "quitar");
    quitar.type = "button";
    quitar.title = "Sacar del equipo";
    quitar.setAttribute("aria-label", `Sacar a ${p.nickname || p.species} del equipo`);
    quitar.addEventListener("click", (evento) => {
      evento.stopPropagation(); // que no cuente como pulsar la casilla (en B3 abrirá la ficha)
      guardarEquipo(equipoActual.filter((q) => q.route !== p.route).map((q) => q.route));
    });

    casilla.addEventListener("click", () => abrirFicha(p, p.alive));
    casilla.addEventListener("keydown", (evento) => {
      if (evento.key === "Enter" || evento.key === " ") {
        evento.preventDefault();
        abrirFicha(p, p.alive);
      }
    });

    // Sin mote, la especie hace de nombre; debajo, siempre la ruta.
    casilla.append(
      quitar,
      figura(p.species_id, !p.alive, 80),
      elemento("div", p.nickname || p.species, "mote"),
      elemento("div", p.route, "ruta")
    );
    return casilla;
  });

  for (let i = casillas.length; i < TAMANO_EQUIPO; i++) {
    const hueco = elemento("button", "+", "hueco");
    hueco.type = "button";
    hueco.setAttribute("aria-label", "Hueco libre: añadir un Pokémon al equipo");
    hueco.append(elemento("small", "Añadir"));
    hueco.addEventListener("click", abrirSelector);
    casillas.push(hueco);
  }
  $("equipo").replaceChildren(...casillas);
}

function abrirSelector() {
  const enEquipo = new Set(equipoActual.map((p) => p.route));
  const libres = vivosActual.filter((p) => !enEquipo.has(p.route));
  const opciones = libres.map((p) => {
    const opcion = elemento("button", undefined, "fila opcion");
    opcion.type = "button";
    const texto = elemento("div", undefined, "texto");
    texto.append(
      elemento("div", p.nickname || p.species, "mote"),
      elemento("div", p.nickname ? p.species : "", "esp"),
      elemento("div", p.route, "ruta")
    );
    opcion.append(texto, figura(p.species_id, false, 64, 1, true));
    opcion.addEventListener("click", () => {
      $("selector").close();
      guardarEquipo([...equipoActual.map((q) => q.route), p.route]);
    });
    const li = elemento("li");
    li.append(opcion);
    return li;
  });
  if (!opciones.length) opciones.push(elemento("li", "No hay Pokémon vivos fuera del equipo.", "vacio"));
  $("selector-lista").replaceChildren(...opciones);
  $("selector").showModal();
}

$("cerrar-selector").addEventListener("click", () => $("selector").close());
// Pulsar fuera de la ventana (en el fondo oscuro) también la cierra
$("selector").addEventListener("click", (evento) => {
  if (evento.target === $("selector")) $("selector").close();
});

async function cargarRun() {
  if (!runActual) return;

  const [equipo, eventos, muertos, party] = await Promise.all([
    pedirConCabeceras(`/runs/${runActual}/team`),
    pedir(`/runs/${runActual}/encounters`),
    pedir(`/runs/${runActual}/graveyard`),
    pedir(`/runs/${runActual}/party`),
  ]);

  const vivos = equipo.cuerpo;
  mostrarInfoCache(equipo.cabeceras);
  vivosActual = vivos;
  equipoActual = party;
  pintarEquipo();

  const capturas = eventos.filter((e) => e.event_type === "captura").length;
  $("contadores").replaceChildren(
    contador("Vivos", vivos.length),
    contador("Muertos", muertos.length, "rojo"),
    contador("Capturas", capturas)
  );
  pintarLista($("vivos"), vivos, false, "Nadie vivo todavía.");
  pintarLista($("cementerio"), muertos, true, "Nadie ha muerto. ¡De momento!");

  pintarFallos(eventos.filter((e) => e.event_type === "fallo"));
}

// ---------- Nueva partida: modo y reglas (ideas 2 + 6) ----------
// El catálogo de reglas y las plantillas vienen del servidor (GET /rules): aquí solo se pintan.
const NOMBRE_MODO = { normal: "Normal", nuzlocke: "Nuzlocke", randomlocke: "Randomlocke" };
const DESCRIPCION_MODO = {
  normal: "Sin reglas: solo llevar el registro de la partida.",
  nuzlocke: "Las reglas clásicas del Nuzlocke.",
  randomlocke: "Nuzlocke con el juego aleatorizado.",
};
const MODO_INICIAL = "randomlocke";
let catalogo = null; // se pide una sola vez

async function cargarCatalogo() {
  if (catalogo) return;
  catalogo = await pedir("/rules");
  pintarModos();
}

function modoElegido() {
  return document.querySelector('input[name="modo"]:checked').value;
}

function pintarModos() {
  $("modos").replaceChildren(...catalogo.modes.map((modo) => {
    const opcion = elemento("label", undefined, "modo-opcion");
    const radio = elemento("input");
    radio.type = "radio";
    radio.name = "modo";
    radio.value = modo;
    radio.addEventListener("change", mostrarReglasDelModo);
    opcion.append(radio, elemento("strong", NOMBRE_MODO[modo]), elemento("small", DESCRIPCION_MODO[modo]));
    return opcion;
  }));
}

// La lista de lo que trae la plantilla del modo elegido (solo lectura)
function mostrarReglasDelModo() {
  const modo = modoElegido();
  const activas = catalogo.rules.filter((r) => r.clave in catalogo.templates[modo]);
  const lista = (titulo, reglas) => {
    if (!reglas.length) return [];
    const ul = elemento("ul", undefined, "lista-reglas");
    ul.append(...reglas.map((r) => elemento("li", r.nombre)));
    return [elemento("h4", titulo), ul];
  };
  $("reglas-modo").replaceChildren(
    ...(activas.length ? [] : [elemento("p", "Ninguna regla activa.", "vacio")]),
    ...lista("Reglas", activas.filter((r) => r.grupo !== "aleatorizado")),
    ...lista("Aleatorizado", activas.filter((r) => r.grupo === "aleatorizado")),
  );
}

async function abrirNuevaPartida() {
  mostrarMensaje("");
  try {
    await cargarCatalogo();
  } catch (error) {
    mostrarMensaje(error.message);
    return;
  }
  $("form-run").reset();
  $("error-run").textContent = "";
  document.querySelector(`input[name="modo"][value="${MODO_INICIAL}"]`).checked = true;
  mostrarReglasDelModo();
  $("dialogo-nueva").showModal();
}

$("form-run").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  $("error-run").textContent = "";
  try {
    const run = await pedir("/runs", enviarJSON({ name: $("nombre-run").value, mode: modoElegido() }));
    $("dialogo-nueva").close();
    location.hash = `#/partida/${run.id}`;
  } catch (error) {
    $("error-run").textContent = error.message; // la ventana sigue abierta: no se pierde lo elegido
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

// ---------- Ficha del Pokémon ----------
const COLOR_TIPO = {
  normal: "#9a9a8e", fire: "#f08030", water: "#6890f0", grass: "#78c850", electric: "#e8b800", ice: "#78c8d0",
  fighting: "#c03028", poison: "#a040a0", ground: "#d8b858", flying: "#8f87e8", psychic: "#f85888", bug: "#a8b820",
  rock: "#b8a038", ghost: "#705898", dragon: "#7038f8", dark: "#705848", steel: "#a0a0c0", fairy: "#e87fa0",
};

async function accionFicha(promesa) {
  $("error-ficha").textContent = "";
  try {
    await promesa;
    $("ficha").close();
    await cargarRun();
  } catch (error) {
    $("error-ficha").textContent = error.message;
  }
}

function boton(texto, clase, alPulsar) {
  const b = elemento("button", texto, "btn" + (clase ? " " + clase : ""));
  b.type = "button";
  b.addEventListener("click", alPulsar);
  return b;
}

// ---------- Ficha editable (C1) ----------
const ESTADISTICAS = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"];
// La naturaleza dice qué estadística sube y cuál baja (nombres de PokéAPI → campos de la ficha)
const CAMPO_ESTADISTICA = {
  attack: "attack", defense: "defense", "special-attack": "sp_attack", "special-defense": "sp_defense", speed: "speed",
};
let naturalezas = null; // se piden una sola vez
let rutaFicha = null;   // ruta del Pokémon cuya ficha está abierta

async function cargarNaturalezas() {
  if (naturalezas) return;
  naturalezas = await pedir("/natures");
  $("f-naturaleza").append(...naturalezas.map((n) => new Option(n.name, n.name)));
}

function marcarNaturaleza() {
  const n = (naturalezas || []).find((x) => x.name === $("f-naturaleza").value);
  for (const fila of document.querySelectorAll(".stat")) {
    const campo = fila.dataset.stat;
    fila.classList.toggle("sube", !!n && CAMPO_ESTADISTICA[n.increased] === campo);
    fila.classList.toggle("baja", !!n && CAMPO_ESTADISTICA[n.decreased] === campo);
  }
}

function pintarBarra(campo) {
  const valor = Number($("f-" + campo).value) || 0;
  $("b-" + campo).style.width = Math.min(100, (valor / 255) * 100) + "%";
}

function rellenarFicha(f) {
  $("f-nivel").value = f.level ?? "";
  $("f-naturaleza").value = f.nature ?? "";
  $("f-habilidad").value = f.ability ?? "";
  $("f-objeto").value = f.item ?? "";
  for (let i = 0; i < 4; i++) $("f-ataque-" + i).value = f.moves[i] ?? "";
  for (const campo of ESTADISTICAS) {
    $("f-" + campo).value = f[campo] ?? "";
    pintarBarra(campo);
  }
  marcarNaturaleza();
  olvidados = f.forgotten;
  pintarAprender();
}

// ---------- Puede aprender y Olvidados (C2) ----------
const ETIQUETA_METODO = { machine: "MT", tutor: "Tutor", egg: "Huevo" };
const aprendizajes = {}; // por especie: no cambian, se piden una sola vez
let aprendizaje = null;  // lo que puede aprender la especie de la ficha abierta
let olvidados = [];      // ataques que tuvo y ya no tiene (los calcula el servidor al guardar)

async function cargarAprendizaje(speciesId) {
  if (!speciesId) return { abilities: [], moves: [] }; // especie desconocida: sin sugerencias
  aprendizajes[speciesId] ??= await pedir(`/species/${speciesId}/learnset`);
  return aprendizajes[speciesId];
}

function huecosAtaque() {
  return [0, 1, 2, 3].map((i) => $("f-ataque-" + i));
}

// Pone el ataque en el primer hueco vacío. Si están los 4 llenos no sustituye ninguno: como en los juegos,
// el jugador decide cuál olvida (lo borra a mano) y al guardar pasa a «Olvidados».
function ponerAtaque(nombre) {
  const libre = huecosAtaque().find((hueco) => !hueco.value.trim());
  if (!libre) {
    $("estado-ficha").textContent = "";
    $("error-ficha").textContent = "Los 4 huecos están ocupados: borra uno primero.";
    return;
  }
  $("error-ficha").textContent = "";
  $("estado-ficha").textContent = "";
  libre.value = nombre;
  pintarAprender();
}

function etiquetaAtaque(nombre, detalle, clase) {
  const etiqueta = elemento("button", nombre, "et" + (clase ? " " + clase : ""));
  etiqueta.type = "button";
  if (detalle) etiqueta.append(elemento("small", detalle));
  etiqueta.addEventListener("click", () => ponerAtaque(nombre));
  return etiqueta;
}

function detalleMetodo(ataque) {
  if (ataque.method !== "level-up") return ETIQUETA_METODO[ataque.method];
  return ataque.level ? `Nv. ${ataque.level}` : "Evo.";
}

// No se sugiere lo que ya está en un hueco
function pintarAprender() {
  const puestos = new Set(huecosAtaque().map((h) => h.value.trim().toLowerCase()).filter(Boolean));
  const filtro = $("filtro-ataques").value.trim().toLowerCase();
  const libres = (nombre) => !puestos.has(nombre.toLowerCase());

  if (!aprendizaje) {
    $("puede-aprender").replaceChildren(elemento("span", "Cargando…", "vacio"));
  } else {
    const lista = aprendizaje.moves.filter((m) => libres(m.name) && m.name.toLowerCase().includes(filtro));
    $("puede-aprender").replaceChildren(
      ...(lista.length ? lista.map((m) => etiquetaAtaque(m.name, detalleMetodo(m)))
                       : [elemento("span", aprendizaje.moves.length ? "Ninguno coincide." : "Sin datos para esta especie.", "vacio")])
    );
  }
  const recuperables = olvidados.filter(libres).reverse(); // el último olvidado, primero
  $("olvidados").replaceChildren(
    ...(recuperables.length ? recuperables.map((m) => etiquetaAtaque(m, "", "olvidado"))
                            : [elemento("span", "Ninguno todavía.", "vacio")])
  );
}

$("filtro-ataques").addEventListener("input", pintarAprender);
// Enter en el buscador no debe guardar la ficha
$("filtro-ataques").addEventListener("keydown", (evento) => {
  if (evento.key === "Enter") evento.preventDefault();
});
for (const hueco of huecosAtaque()) hueco.addEventListener("input", pintarAprender);

async function cargarFicha(ruta, speciesId) {
  rutaFicha = ruta;
  aprendizaje = null;
  olvidados = [];
  $("form-ficha").reset();
  $("estado-ficha").textContent = "";
  $("lista-habilidades").replaceChildren();
  pintarAprender();
  try {
    await cargarNaturalezas();
    const [ficha, datos] = await Promise.all([
      pedir(`/runs/${runActual}/sheet?route=${encodeURIComponent(ruta)}`),
      cargarAprendizaje(speciesId),
    ]);
    if (rutaFicha !== ruta) return; // por si se abrió otra ficha mientras tanto
    aprendizaje = datos;
    $("lista-habilidades").replaceChildren(
      ...datos.abilities.map((h) => new Option(h.hidden ? "Habilidad oculta" : "", h.name))
    );
    rellenarFicha(ficha);
  } catch (error) {
    $("error-ficha").textContent = error.message;
  }
}

function numeroONulo(id) {
  const texto = $(id).value.trim();
  return texto === "" ? null : Number(texto);
}

$("form-ficha").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  $("error-ficha").textContent = "";
  $("estado-ficha").textContent = "";
  const datos = {
    level: numeroONulo("f-nivel"),
    nature: $("f-naturaleza").value || null,
    ability: $("f-habilidad").value.trim() || null,
    item: $("f-objeto").value.trim() || null,
    moves: [0, 1, 2, 3].map((i) => $("f-ataque-" + i).value.trim()).filter(Boolean),
  };
  for (const campo of ESTADISTICAS) datos[campo] = numeroONulo("f-" + campo);
  try {
    const guardada = await pedir(`/runs/${runActual}/sheet?route=${encodeURIComponent(rutaFicha)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });
    rellenarFicha(guardada);
    $("estado-ficha").textContent = "Guardado ✓";
  } catch (error) {
    $("error-ficha").textContent = error.message;
  }
});

$("f-naturaleza").addEventListener("change", marcarNaturaleza);
for (const campo of ESTADISTICAS) $("f-" + campo).addEventListener("input", () => pintarBarra(campo));

function abrirFicha(p, vivo) {
  const enEquipo = equipoActual.some((q) => q.route === p.route);
  $("error-ficha").textContent = "";
  cargarFicha(p.route, p.species_id);
  $("ficha-dibujo").replaceChildren(figura(p.species_id, !vivo, 112, 1, true));
  $("ficha-nombre").textContent = p.nickname || p.species;
  $("ficha-sub").textContent = (p.nickname ? p.species + " · " : "") + p.route;
  $("ficha-tipos").replaceChildren(
    ...(p.types || []).map((t) => {
      const etiqueta = elemento("span", t.name, "tipo");
      etiqueta.style.background = COLOR_TIPO[t.identifier] || "#777";
      return etiqueta;
    })
  );
  const estado = [elemento("span", vivo ? "Vivo" : "Muerto", "marca-estado" + (vivo ? "" : " muerto"))];
  if (enEquipo) estado.push(elemento("span", "En el equipo", "marca-estado"));
  $("ficha-estado").replaceChildren(...estado);

  // Solo las acciones que tienen sentido en cada caso
  const acciones = [];
  if (vivo) {
    acciones.push(boton("Ha muerto", "primario", () =>
      accionFicha(pedir(`/runs/${runActual}/events`,
        enviarJSON({ event_type: "muerte", route: p.route, species: p.species })))));
  } else {
    acciones.push(boton("Revivir", "", () =>
      accionFicha(pedir(`/runs/${runActual}/deaths?route=${encodeURIComponent(p.route)}`, { method: "DELETE" }))));
  }
  if (enEquipo) {
    acciones.push(boton("Sacar del equipo", "", () => {
      $("ficha").close();
      guardarEquipo(equipoActual.filter((q) => q.route !== p.route).map((q) => q.route));
    }));
  } else if (vivo && equipoActual.length < TAMANO_EQUIPO) {
    acciones.push(boton("Añadir al equipo", "", () => {
      $("ficha").close();
      guardarEquipo([...equipoActual.map((q) => q.route), p.route]);
    }));
  }
  acciones.push(boton("Eliminar", "peligro", () => {
    $("ficha").close();
    eliminarEncuentro(p.route, `${p.nickname || p.species} (${p.route})`);
  }));
  $("ficha-acciones").replaceChildren(...acciones);
  $("ficha").showModal();
}

$("cerrar-ficha").addEventListener("click", () => $("ficha").close());
$("ficha").addEventListener("click", (evento) => {
  if (evento.target === $("ficha")) $("ficha").close();
});

// Eliminar borra de verdad (decisión A): por eso se pide confirmación antes.
async function eliminarEncuentro(ruta, descripcion) {
  if (!confirm(`¿Eliminar ${descripcion}? Se borra por completo (también su muerte y su sitio en el equipo) y no se puede deshacer.`)) return;
  mostrarMensaje("");
  try {
    await pedir(`/runs/${runActual}/encounters?route=${encodeURIComponent(ruta)}`, { method: "DELETE" });
  } catch (error) {
    mostrarMensaje(error.message);
  }
  await cargarRun();
}

// ---------- Nuevo encuentro (ventana) ----------
// Nuevo encuentro: captura o fallo (la muerte se marca desde la ficha del Pokémon).
// El mote solo tiene sentido en una captura: el campo se oculta en un fallo.
function ajustarFormularioEvento() {
  $("campo-mote").hidden = $("tipo-evento").value !== "captura";
}

$("abrir-registro").addEventListener("click", () => {
  $("form-evento").reset();
  $("error-evento").textContent = "";
  ajustarFormularioEvento();
  $("dialogo-evento").showModal();
  $("ruta").focus();
});

$("tipo-evento").addEventListener("change", ajustarFormularioEvento);

$("cancelar-evento").addEventListener("click", () => $("dialogo-evento").close());

$("form-evento").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  $("error-evento").textContent = "";
  const datos = { event_type: $("tipo-evento").value, route: $("ruta").value, species: $("especie").value };
  const mote = $("mote").value.trim();
  if (datos.event_type === "captura" && mote) datos.nickname = mote;
  try {
    await pedir(`/runs/${runActual}/events`, enviarJSON(datos));
    $("dialogo-evento").close();
    await cargarRun();
  } catch (error) {
    // El error se enseña dentro de la ventana, que sigue abierta para corregir el dato
    $("error-evento").textContent = error.message;
  }
});

navegar();
