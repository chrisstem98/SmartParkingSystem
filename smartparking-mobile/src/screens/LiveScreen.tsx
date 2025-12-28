import { useEffect, useMemo, useState } from "react";
import {
  View,
  Text,
  Image,
  ActivityIndicator,
  ScrollView,
  RefreshControl,
  Pressable,
  StyleSheet,
} from "react-native";
import { fetchParkingLots, ParkingLot } from "../services/parkingLots";
import { fetchLive } from "../services/live";
import { LiveResponse } from "../types/live";
import ParkingPickerModal from "../components/ParkingPickerModal";

export default function LiveScreen() {
  const [lots, setLots] = useState<ParkingLot[]>([]);
  const [selectedSite, setSelectedSite] = useState<string>(""); // required by backend
  const [pickerOpen, setPickerOpen] = useState(false);

  const [data, setData] = useState<LiveResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  async function loadLots() {
    const res = await fetchParkingLots();
    setLots(res);

    // Auto-select the first lot if none selected yet
    if (!selectedSite && res.length > 0) {
      setSelectedSite(res[0].code);
    }
  }

  async function loadLive() {
    if (!selectedSite) return;

    try {
      setError("");
      const res = await fetchLive(selectedSite);
      setData(res);
    } catch (e) {
      setError("Failed to load live data.");
    } finally {
      setLoading(false);
    }
  }

  // Initial load: fetch parking lots (and auto-select first lot)
  useEffect(() => {
    loadLots().catch(() => setError("Failed to load parking lots."));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load live whenever selectedSite changes
  useEffect(() => {
    if (!selectedSite) return;
    setLoading(true);
    loadLive();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSite]);

  // Polling every 4 seconds (near-real-time)
  useEffect(() => {
    if (!selectedSite) return;
    const id = setInterval(() => {
      loadLive();
    }, 4000);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSite]);

  const occupancyText = useMemo(() => {
    if (!data) return "";
    return `Occupied: ${data.latest_snapshot.occupied} • Empty: ${data.latest_snapshot.empty}`;
  }, [data]);

  const selectedLotLabel = useMemo(() => {
    const found = lots.find((l) => l.code === selectedSite);
    return found ? `${found.name} (${found.code})` : selectedSite || "Select parking";
  }, [lots, selectedSite]);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadLive();
    setRefreshing(false);
  };

  if (loading && !data) {
    return (
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
        <ActivityIndicator />
        <Text style={{ marginTop: 8 }}>Loading live view…</Text>
      </View>
    );
  }

  return (
    <ScrollView
      contentContainerStyle={{ padding: 16, gap: 12 }}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <Text style={{ fontSize: 22, fontWeight: "700" }}>Live</Text>

      {/* Parking dropdown button */}
      <View style={styles.card}>
        <Text style={styles.cardLabel}>Parking</Text>

        <Pressable style={styles.dropdownBtn} onPress={() => setPickerOpen(true)}>
          <Text style={styles.dropdownText}>{selectedLotLabel}</Text>
          <Text style={styles.dropdownArrow}>▾</Text>
        </Pressable>
      </View>

      {/* Modal picker */}
      <ParkingPickerModal
        visible={pickerOpen}
        lots={lots}
        selectedCode={selectedSite}
        onSelect={(code) => setSelectedSite(code)}
        onClose={() => setPickerOpen(false)}
      />

      {/* Error */}
      {error ? <Text style={{ color: "red" }}>{error}</Text> : null}

      {/* Live snapshot card */}
      {data ? (
        <View style={[styles.card, { gap: 6 }]}>
          <Text style={{ opacity: 0.7 }}>Site</Text>
          <Text style={{ fontSize: 18, fontWeight: "700" }}>{data.site}</Text>

          <Text style={{ marginTop: 8, opacity: 0.7 }}>Timestamp</Text>
          <Text>{data.latest_snapshot.timestamp}</Text>

          <Text style={{ marginTop: 10, fontWeight: "700" }}>
            {occupancyText}
          </Text>

          <Image
            source={{ uri: data.latest_snapshot.annotated_url }}
            style={{ width: "100%", height: 260, borderRadius: 10, marginTop: 12 }}
            resizeMode="cover"
          />
        </View>
      ) : (
        <Text style={{ opacity: 0.7 }}>No live data yet.</Text>
      )}
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
  cardLabel: {
    fontSize: 13,
    opacity: 0.7,
    marginBottom: 8,
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
  dropdownText: {
    fontSize: 16,
    fontWeight: "600",
  },
  dropdownArrow: {
    fontSize: 18,
    opacity: 0.7,
    marginLeft: 10,
  },
});
