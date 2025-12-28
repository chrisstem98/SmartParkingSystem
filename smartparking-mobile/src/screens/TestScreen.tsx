import { useEffect, useState } from "react";
import { View, Text } from "react-native";
import { fetchParkingLots, ParkingLot } from "../services/parkingLots";

export default function TestScreen() {
  const [lots, setLots] = useState<ParkingLot[]>([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    fetchParkingLots()
      .then(setLots)
      .catch(() => setErr("Failed to fetch parking lots from backend"));
  }, []);

  return (
    <View style={{ padding: 16, gap: 8 }}>
      <Text style={{ fontSize: 20, fontWeight: "600" }}>Backend Connection Test</Text>

      {err ? <Text style={{ color: "red" }}>{err}</Text> : null}

      {lots.map((l) => (
        <Text key={l.code}>
          {l.name} ({l.code})
        </Text>
      ))}
    </View>
  );
}
