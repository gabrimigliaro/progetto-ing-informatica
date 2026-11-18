from fastapi.concurrency import run_in_threadpool #type: ignore

from assets.crud import ws as ws_crud
from api.endpoints.notifications import send_push_to_all_subscribers

'''
export const EMERGENCY_TYPES = [
        {
            id: 1,
            label: 'Caduta rilevata',
            class: styles.red,
            icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>,
            badge: <CardAlert type={"fall"} />
        },
        {
            id: 2,
            label: 'Battiti troppo alti',
            class: styles.red,
            icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>,
            badge: <CardAlert type={"heartBeatH"} />
        },
        {
            id: 3,
            label: 'Battiti troppo bassi',
            class: styles.red,
            icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>,
            badge: <CardAlert type={"heartBeatL"} />
        },
        {
            id: 4,
            label: 'Supporto richiesto',
            class: styles.yellow,
            icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><path d="m4.93 4.93 4.24 4.24"></path><path d="m14.83 9.17 4.24-4.24"></path><path d="m14.83 14.83 4.24 4.24"></path><path d="m9.17 14.83-4.24 4.24"></path><circle cx="12" cy="12" r="4"></circle></svg>,
            badge: <CardAlert type={"support"} />
        },
];
'''

EMERGENCY_LABELS = {1: "Caduta", 2: "Battiti alti", 3: "Battiti bassi", 4: "Supporto generico"}

async def parsePacket(raw_data: list[str], manager):
    raw_data = raw_data.strip()

    if raw_data.startswith("{"): return

    data = [item.strip() for item in raw_data.split(",")]

    packetType = int(data[0])

    if packetType == 0:
        print("Arrivato pacchetto di tipo 0.")
        mac_address = data[2]

        saved_device = await run_in_threadpool(ws_crud.save_device_to_db, mac_address)

        if saved_device.get("status") == "error":
            await manager.broadcast_to_dashboards({"event": "NEW_DEVICE_ERROR", "payload": saved_device["message"]})
        else: await manager.broadcast_to_dashboards({"event": "NEW_DEVICE", "payload": saved_device})

    elif packetType == 10:
        print("Arrivato pacchetto di tipo 10.")

        apName = data[1]
        deviceUid = data[2]
        bpm = data[3]
        battery = data[4]
        steps = data[5]
        emergency = int(data[6])
        fall = int(data[7])

        payload = {}
        patient = None

        patient = ws_crud.get_patient_by_device_id(deviceUid)
        if not patient:
            print("Paziente non associato ad alcun dispositivo.")
            return

        if emergency == 1:
            saved_emergency = await run_in_threadpool(ws_crud.save_emergency_to_db, patient["id"], 4, int(bpm))

            await manager.broadcast_to_dashboards({"event": "NEW_EMERGENCY", "payload": saved_emergency})

            patient_name = (f"{saved_emergency['patient']['name']} {saved_emergency['patient']['surname']}")
            patient_id = saved_emergency['patient']['id']

            label = EMERGENCY_LABELS.get(5, "Emergenza")

            #await run_in_threadpool(send_push_to_all_subscribers, f"🚨 {label}", f"Rilevata per {patient_name}", f"/dashboard/patient/{patient_id}")
        elif fall == 1:
            saved_emergency = await run_in_threadpool(ws_crud.save_emergency_to_db, patient["id"], 1, int(bpm))

            await manager.broadcast_to_dashboards({"event": "NEW_EMERGENCY", "payload": saved_emergency})

            patient_name = (f"{saved_emergency['patient']['name']} {saved_emergency['patient']['surname']}")
            patient_id = saved_emergency['patient']['id']

            label = EMERGENCY_LABELS.get(1, "Emergenza")

            #await run_in_threadpool(send_push_to_all_subscribers, f"🚨 {label}", f"Rilevata per {patient_name}", f"/dashboard/patient/{patient_id}")
        elif int(bpm) <= 40:
            saved_emergency = await run_in_threadpool(ws_crud.save_emergency_to_db, patient["id"], 3, int(bpm))

            await manager.broadcast_to_dashboards({"event": "NEW_EMERGENCY", "payload": saved_emergency})

            patient_name = (f"{saved_emergency['patient']['name']} {saved_emergency['patient']['surname']}")
            patient_id = saved_emergency['patient']['id']

            label = EMERGENCY_LABELS.get(3, "Emergenza")

            #await run_in_threadpool(send_push_to_all_subscribers, f"🚨 {label}", f"Rilevata per {patient_name}", f"/dashboard/patient/{patient_id}")
        elif int(bpm) >= 140:
            saved_emergency = await run_in_threadpool(ws_crud.save_emergency_to_db, patient["id"], 2, int(bpm))

            await manager.broadcast_to_dashboards({"event": "NEW_EMERGENCY", "payload": saved_emergency})

            patient_name = (f"{saved_emergency['patient']['name']} {saved_emergency['patient']['surname']}")
            patient_id = saved_emergency['patient']['id']

            label = EMERGENCY_LABELS.get(2, "Emergenza")

            #await run_in_threadpool(send_push_to_all_subscribers, f"🚨 {label}", f"Rilevata per {patient_name}", f"/dashboard/patient/{patient_id}")
        
        payload = {
            "device_id": deviceUid,
            "bpm": bpm,
            "battery": battery,
            "steps": steps,
            "emergency": emergency,
            "fall": fall,
            "patient": patient,
        }

        await manager.broadcast_to_dashboards({"event": "DEVICE_UPDATE", "payload": payload})