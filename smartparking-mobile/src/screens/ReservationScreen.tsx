import { useEffect, useMemo, useState } from "react";
import { View, Text, Pressable, StyleSheet, Alert, ActivityIndicator, ScrollView } from "react-native";
import DateTimePicker from "@react-native-community/datetimepicker";

import ParkingPickerModal from "../components/ParkingPickerModal";
import { fetchParkingLots, ParkingLot } from "../services/parkingLots";
import { getDeviceId } from "../services/device";
import { createReservation } from "../services/reservations";

function addMinutes(date: Date, minutes: number) {
  return new Date(date.getTime() + minutes * 60 * 1000);
}

export default function ReservationScreen() {
  const [lots, setLots] = useState<ParkingLot[]>([]);
  const [selectedSite, setSelectedSite] = useState<string>("");
  const [pickerOpen, setPickerOpen] = useState(false);

  // Default: start = now + 5min, duration = 30min
  const [start, setStart] = useState<Date>(addMinutes(new Date(), 5));
  const [durationMin, setDurationMin] = useState<number>(30);

  const [showStartPicker, setShowStartPicker] = useState(false);

  const [deviceId, setDeviceId] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    (async () => {
      const [lotRes, dev] = await Promise.all([fetchParkingLots(), getDeviceId()]);
      setLots(lotRes);
      setDeviceId(dev);

      if (lotRes.length > 0) {
        setSelectedSite(lotRes[0].code);
      }
    })().catch(() => {
      Alert.alert("Error", "Failed to initialize reservations screen.");
    });
  }, []);

  const end = useMemo(() => addMinutes(start, durationMin), [start, durationMin]);

  const selectedLotLabel = useMemo(() => {
    const found = lots.find((l) => l.code === selectedSite);
    return found ? `${found.name} (${found.code})` : selectedSite || "Select parking";
  }, [lots, selectedSite]);

  const startLabel = useMemo(() => start.toLocaleString(), [start]);
  const endLabel = useMemo(() => end.toLocaleString(), [end]);

  async function onSubmit() {
    if (!selectedSite) {
      Alert.alert("Missing parking", "Please select a parking lot.");
      return;
    }
    if (!deviceId) {
      Alert.alert("Error", "Device ID not ready yet.");
      return;
    }

    const now = new Date();
    if (start.getTime() < now.getTime()) {
      Alert.alert("Invalid time", "Start time cannot be in the past.");
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        site: selectedSite,
        device_id: deviceId,
        start_time: start.toISOString(),
        end_time: end.toISOString(),
      };

      const res = await createReservation(payload);

      Alert.alert(
        "Reservation created",
        `Reservation #${res.id}\n${res.site}\n${startLabel} → ${endLabel}`
      );
    } catch (e: any) {
      const msg =
        e?.response?.data?.error ||
        "Reservation failed. Please try again.";
      Alert.alert("Error", msg);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <ScrollView contentContainerStyle={{ padding: 16, gap: 12 }}>
      <Text style={{ fontSize: 22, fontWeight: "700" }}>Make a Reservation</Text>

      {/* Parking selector */}
      <View style={styles.card}>
        <Text style={styles.label}>Parking</Text>
        <Pressable style={styles.dropdownBtn} onPress={() => setPickerOpen(true)}>
          <Text style={styles.dropdownText}>{selectedLotLabel}</Text>
          <Text style={styles.dropdownArrow}>▾</Text>
        </Pressable>
      </View>

      <ParkingPickerModal
        visible={pickerOpen}
        lots={lots}
        selectedCode={selectedSite}
        onSelect={(code) => setSelectedSite(code)}
        onClose={() => setPickerOpen(false)}
      />

      {/* Duration */}
      <View style={styles.card}>
        <Text style={styles.label}>Duration</Text>
        <View style={{ flexDirection: "row", gap: 8, marginTop: 8 }}>
          {[15, 30, 60, 90, 120].map((m) => {
            const active = durationMin === m;
            return (
              <Pressable
                key={m}
                onPress={() => setDurationMin(m)}
                style={[styles.pill, active && styles.pillActive]}
              >
                <Text style={[styles.pillText, active && styles.pillTextActive]}>
                  {m}m
                </Text>
              </Pressable>
            );
          })}
        </View>

        <Text style={{ marginTop: 10, opacity: 0.7 }}>
          End time: {endLabel}
        </Text>
      </View>

      {/* Submit */}
      <Pressable
        onPress={onSubmit}
        disabled={submitting || !deviceId || !selectedSite}
        style={[styles.submitBtn, (submitting || !deviceId || !selectedSite) && styles.submitDisabled]}
      >
        {submitting ? (
          <View style={{ flexDirection: "row", alignItems: "center", gap: 10 }}>
            <ActivityIndicator />
            <Text style={styles.submitText}>Reserving…</Text>
          </View>
        ) : (
          <Text style={styles.submitText}>Reserve</Text>
        )}
      </Pressable>

      <Text style={{ marginTop: 6, opacity: 0.55, fontSize: 12 }}>
        Device ID (for MVP): {deviceId ? deviceId : "loading..."}
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 12,
    borderWidth: 1,
    borderRadius: 12,
    borderColor: "#e5e7eb",
    backgroundColor: "white",
  },
  label: {
    fontSize: 13,
    opacity: 0.7,
    marginBottom: 8,
    fontWeight: "600",
  },
  dropdownBtn: {
    paddingVertical: 12,
    paddingHorizontal: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#e5e7eb",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  dropdownText: { fontSize: 16, fontWeight: "600" },
  dropdownArrow: { fontSize: 18, opacity: 0.7, marginLeft: 10 },
  rowBtn: {
    paddingVertical: 12,
    paddingHorizontal: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#e5e7eb",
  },
  rowText: { fontSize: 16, fontWeight: "600" },
  pill: {
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: "#e5e7eb",
  },
  pillActive: {
    backgroundColor: "#EEF2FF",
    borderColor: "#C7D2FE",
  },
  pillText: { fontWeight: "700" },
  pillTextActive: { color: "#1D4ED8" },
  submitBtn: {
    marginTop: 6,
    paddingVertical: 14,
    borderRadius: 14,
    alignItems: "center",
    backgroundColor: "#2563eb",
  },
  submitDisabled: { opacity: 0.5 },
  submitText: { color: "white", fontWeight: "800", fontSize: 16 },
});
