import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="Multiagente Visual - Vehículos")

# Primera versión: clasificación por palabras clave.
# Después la reemplazaremos por un orquestador con IA.

AGENTES = {
    "consumo": ["consumo", "gasolina", "combustible",
                "eficiencia", "ahorro", "ahorrador"],
    "comodidad": ["comodidad", "comodo", "cómodo",
                  "familia", "espacio", "maletero"],
    "seguridad": ["seguridad", "seguro", "airbag",
                  "frenos", "protección"],
    "costos": ["precio", "presupuesto", "costo",
               "económico", "economico", "barato"],
    "rendimiento": ["potencia", "rendimiento",
                    "motor", "velocidad", "torque"]
}


def seleccionar_agentes(pregunta):
    pregunta = pregunta.lower()

    seleccionados = [
        agente
        for agente, palabras in AGENTES.items()
        if any(palabra in pregunta for palabra in palabras)
    ]

    # Si no reconoce una especialidad, usa una ruta general.
    return seleccionados or list(AGENTES.keys())


async def procesar_agente(websocket, agente):
    await websocket.send_json({
        "type": "agent_started",
        "agent": agente,
        "message": f"El agente {agente} inició su análisis."
    })

    # Simula el tiempo de trabajo del agente.
    await asyncio.sleep(2)

    resultado = (
        f"El agente {agente} completó su análisis "
        "(resultado simulado)."
    )

    await websocket.send_json({
        "type": "agent_completed",
        "agent": agente,
        "message": resultado
    })

    return resultado


@app.get("/")
def inicio():
    return {
        "status": "ok",
        "message": " Hola Sami, el backend si está activo"
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            mensaje = json.loads(data)
            pregunta = mensaje.get("question", "").strip()

            if not pregunta:
                await websocket.send_json({
                    "type": "error",
                    "message": "La pregunta está vacía."
                })
                continue

            await websocket.send_json({
                "type": "orchestrator_started",
                "message": "Analizando la solicitud del usuario..."
            })

            await asyncio.sleep(1)

            agentes = seleccionar_agentes(pregunta)

            await websocket.send_json({
                "type": "routing_decision",
                "agents": agentes,
                "message": (
                    "He seleccionado los siguientes agentes: "
                    + ", ".join(agentes)
                )
            })

            # Ejecutar los agentes seleccionados en paralelo.
            resultados = await asyncio.gather(
                *[
                    procesar_agente(websocket, agente)
                    for agente in agentes
                ]
            )

            await websocket.send_json({
                "type": "integration_started",
                "message": (
                    "Todos los agentes terminaron. "
                    "Integrando sus resultados..."
                )
            })

            await asyncio.sleep(1)

            await websocket.send_json({
                "type": "final_response",
                "message": "\n".join(resultados)
            })

    except WebSocketDisconnect:
        print("Cliente desconectado")