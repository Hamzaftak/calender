
import streamlit as st
import pandas as pd
from streamlit_calendar import calendar

st.set_page_config(
    page_title="CLINICOG",
    page_icon="📅",
    layout="wide",
)

# Temporary in-memory data
if "patients" not in st.session_state:
    st.session_state.patients = {
        1: {
            "nom": "Dupont",
            "prenom": "Marie",
            "date_naissance": "1990-05-12",
            "anamnese": "",
        },
        2: {
            "nom": "Martin",
            "prenom": "Paul",
            "date_naissance": "1985-09-20",
            "anamnese": "",
        },
    }

if "appointments" not in st.session_state:
    st.session_state.appointments = [
        {
            "id": 1,
            "patient_id": 1,
            "psy": "Dr. Bernard",
            "date": "2026-10-16",
            "heure": "10:00",
            "duree": 45,
            "motif": "Consultation",
            "statut": "Confirmé",
        },
        {
            "id": 2,
            "patient_id": 2,
            "psy": "Dr. Bernard",
            "date": "2026-10-16",
            "heure": "11:00",
            "duree": 60,
            "motif": "Suivi",
            "statut": "Confirmé",
        },
    ]

if "next_patient_id" not in st.session_state:
    st.session_state.next_patient_id = 3

if "next_appointment_id" not in st.session_state:
    st.session_state.next_appointment_id = 3


patients = st.session_state.patients
appointments = st.session_state.appointments


def patient_name(patient_id):
    p = patients[patient_id]
    return f"{p['prenom']} {p['nom']}"


st.title("CLINICOG")
st.caption("Gestion des rendez-vous et dossiers patients")

page = st.sidebar.radio(
    "Navigation",
    ["Calendrier", "Patients", "Nouveau rendez-vous"],
)

# --------------------------------------------------
# CALENDAR
# --------------------------------------------------
if page == "Calendrier":
    st.header("Calendrier des rendez-vous")

    psy_filter = st.selectbox(
        "Psychologue",
        ["Tous"] + sorted(
            set(a["psy"] for a in appointments)
            | {"Dr. Bernard", "Dr. Dupont"}
        ),
    )

    visible_appointments = [
        a for a in appointments
        if psy_filter == "Tous" or a["psy"] == psy_filter
    ]

    events = []
    for a in visible_appointments:
        if a["statut"] == "Annulé":
            continue

        events.append({
            "id": str(a["id"]),
            "title": patient_name(a["patient_id"]),
            "start": f"{a['date']}T{a['heure']}:00",
            "end": (
                pd.Timestamp(f"{a['date']}T{a['heure']}")
                + pd.Timedelta(minutes=a["duree"])
            ).isoformat(),
            "backgroundColor": "#3788d8",
        })

    calendar_options = {
        "initialView": "timeGridWeek",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay",
        },
        "slotMinTime": "08:00:00",
        "slotMaxTime": "20:00:00",
        "selectable": True,
        "height": 650,
        "locale": "fr",
    }

    calendar(
        events=events,
        options=calendar_options,
        key="clinic_calendar",
    )

    st.subheader("Liste des rendez-vous")

    if not visible_appointments:
        st.info("Aucun rendez-vous.")
    else:
        for a in sorted(
            visible_appointments,
            key=lambda x: (x["date"], x["heure"])
        ):
            if a["statut"] == "Annulé":
                continue

            with st.expander(
                f"{a['date']} à {a['heure']} — "
                f"{patient_name(a['patient_id'])}"
            ):
                st.write(f"**Psychologue :** {a['psy']}")
                st.write(f"**Durée :** {a['duree']} minutes")
                st.write(f"**Motif :** {a['motif']}")
                st.write(f"**Statut :** {a['statut']}")

                if st.button(
                    "Voir le dossier patient",
                    key=f"patient_{a['id']}",
                ):
                    st.session_state.selected_patient = a["patient_id"]
                    st.session_state.page_patient = True
                    st.rerun()

                if st.button(
                    "Annuler le rendez-vous",
                    key=f"cancel_{a['id']}",
                ):
                    a["statut"] = "Annulé"
                    st.rerun()

    if st.session_state.get("page_patient"):
        pid = st.session_state.pop("selected_patient")
        st.session_state.page_patient = False
        st.session_state.patient_to_open = pid
        st.rerun()

    if st.session_state.get("patient_to_open") in patients:
        pid = st.session_state.patient_to_open
        p = patients[pid]

        st.divider()
        st.subheader(f"Dossier : {patient_name(pid)}")
        st.write(f"Date de naissance : {p['date_naissance']}")
        st.text_area(
            "Anamnèse",
            key=f"anamnese_{pid}",
            value=p["anamnese"],
        )
        if st.button("Enregistrer l'anamnèse", key=f"save_{pid}"):
            p["anamnese"] = st.session_state[f"anamnese_{pid}"]
            st.success("Anamnèse enregistrée.")
        if st.button("Fermer le dossier"):
            del st.session_state.patient_to_open
            st.rerun()


# --------------------------------------------------
# PATIENTS
# --------------------------------------------------
elif page == "Patients":
    st.header("Dossiers patients")

    with st.expander("Ajouter un patient"):
        with st.form("new_patient"):
            prenom = st.text_input("Prénom")
            nom = st.text_input("Nom")
            naissance = st.date_input(
                "Date de naissance",
                value=pd.Timestamp("1990-01-01").date(),
            )

            submitted = st.form_submit_button("Créer le patient")

            if submitted:
                if not prenom.strip() or not nom.strip():
                    st.error("Le nom et le prénom sont obligatoires.")
                else:
                    pid = st.session_state.next_patient_id
                    patients[pid] = {
                        "prenom": prenom.strip(),
                        "nom": nom.strip(),
                        "date_naissance": naissance.isoformat(),
                        "anamnese": "",
                    }
                    st.session_state.next_patient_id += 1
                    st.success("Patient créé.")
                    st.rerun()

    search = st.text_input("Rechercher un patient")

    for pid, p in patients.items():
        name = f"{p['prenom']} {p['nom']}"

        if search.lower() not in name.lower():
            continue

        with st.expander(name):
            st.write(f"Date de naissance : {p['date_naissance']}")

            history = [
                a for a in appointments
                if a["patient_id"] == pid
            ]

            st.write(f"Nombre de rendez-vous : {len(history)}")

            st.subheader("Anamnèse")
            anamnese = st.text_area(
                "Notes cliniques",
                value=p["anamnese"],
                key=f"patient_anamnese_{pid}",
            )

            if st.button("Enregistrer", key=f"patient_save_{pid}"):
                p["anamnese"] = anamnese
                st.success("Dossier enregistré.")

            st.subheader("Historique des rendez-vous")
            if history:
                st.dataframe(
                    pd.DataFrame([
                        {
                            "Date": a["date"],
                            "Heure": a["heure"],
                            "Psychologue": a["psy"],
                            "Motif": a["motif"],
                            "Statut": a["statut"],
                        }
                        for a in history
                    ]),
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                st.info("Aucun rendez-vous.")


# --------------------------------------------------
# NEW APPOINTMENT
# --------------------------------------------------
elif page == "Nouveau rendez-vous":
    st.header("Créer un rendez-vous")

    with st.form("new_appointment"):
        patient_options = {
            f"{p['prenom']} {p['nom']} (ID {pid})": pid
            for pid, p in patients.items()
        }

        selected_patient = st.selectbox(
            "Patient",
            list(patient_options.keys()),
        )

        psy = st.selectbox(
            "Psychologue",
            ["Dr. Bernard", "Dr. Dupont"],
        )

        date = st.date_input("Date")
        heure = st.time_input(
            "Heure",
            value=pd.Timestamp("09:00").time(),
        )

        duree = st.selectbox(
            "Durée",
            [30, 45, 60, 90],
            index=1,
        )

        motif = st.selectbox(
            "Motif",
            ["Consultation", "Suivi", "Première consultation", "Autre"],
        )

        submitted = st.form_submit_button("Créer le rendez-vous")

        if submitted:
            pid = patient_options[selected_patient]
            start = pd.Timestamp(
                f"{date.isoformat()}T{heure.strftime('%H:%M')}"
            )
            end = start + pd.Timedelta(minutes=duree)

            conflict = False

            for a in appointments:
                if a["psy"] != psy or a["statut"] == "Annulé":
                    continue

                existing_start = pd.Timestamp(
                    f"{a['date']}T{a['heure']}"
                )
                existing_end = existing_start + pd.Timedelta(
                    minutes=a["duree"]
                )

                if start < existing_end and end > existing_start:
                    conflict = True
                    break

            if conflict:
                st.error(
                    "Ce psychologue a déjà un rendez-vous sur ce créneau."
                )
            else:
                appointments.append({
                    "id": st.session_state.next_appointment_id,
                    "patient_id": pid,
                    "psy": psy,
                    "date": date.isoformat(),
                    "heure": heure.strftime("%H:%M"),
                    "duree": duree,
                    "motif": motif,
                    "statut": "Confirmé",
                })

                st.session_state.next_appointment_id += 1
                st.success("Rendez-vous créé.")
                st.rerun()
