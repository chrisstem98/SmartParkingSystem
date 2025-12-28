import React, { useMemo, useState } from "react";
import {
  Modal,
  View,
  Text,
  Pressable,
  FlatList,
  StyleSheet,
  TextInput,
  Platform,
} from "react-native";
import * as Haptics from "expo-haptics";
import type { ParkingLot } from "../services/parkingLots";

type Props = {
  visible: boolean;
  lots: ParkingLot[];
  selectedCode: string;
  onSelect: (code: string) => void;
  onClose: () => void;
};

// How many items to show in "Recently used"
const RECENT_MAX = 3;

export default function ParkingPickerModal({
  visible,
  lots,
  selectedCode,
  onSelect,
  onClose,
}: Props) {
  const [query, setQuery] = useState("");
  const [recent, setRecent] = useState<string[]>([]);

  // Normalize text for search (case-insensitive)
  const q = query.trim().toLowerCase();

  // Filtered lots based on search query
  const filtered = useMemo(() => {
    if (!q) return lots;

    return lots.filter((l) => {
      const hay = `${l.name} ${l.code}`.toLowerCase();
      return hay.includes(q);
    });
  }, [lots, q]);

  const recentLots = useMemo(() => {
    const set = new Set(recent);
    const list = lots.filter((l) => set.has(l.code));
    // keep order as in recent array
    list.sort((a, b) => recent.indexOf(a.code) - recent.indexOf(b.code));
    return list.slice(0, RECENT_MAX);
  }, [lots, recent]);

  const triggerHaptic = async () => {
    try {
      // Light selection haptic (safe no-op on unsupported)
      await Haptics.selectionAsync();
    } catch {
      // ignore
    }
  };

  const handleSelect = async (code: string) => {
    await triggerHaptic();

    // Update recent list: move code to front, keep unique, cap size
    setRecent((prev) => {
      const next = [code, ...prev.filter((c) => c !== code)];
      return next.slice(0, RECENT_MAX);
    });

    onSelect(code);
    onClose();
  };

  // Reset search when opening/closing (optional: keeps UX clean)
  const handleClose = async () => {
    await triggerHaptic();
    setQuery("");
    onClose();
  };

  const renderLotItem = ({ item }: { item: ParkingLot }) => {
    const isSelected = item.code === selectedCode;

    return (
      <Pressable
        onPress={() => handleSelect(item.code)}
        style={[styles.item, isSelected && styles.itemSelected]}
      >
        <View>
          <Text style={[styles.itemTitle, isSelected && styles.itemTitleSelected]}>
            {item.name}
          </Text>
          <Text style={[styles.itemSubtitle, isSelected && styles.itemSubtitleSelected]}>
            {item.code}
          </Text>
        </View>

        {isSelected ? <Text style={styles.check}>✓</Text> : null}
      </Pressable>
    );
  };

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={handleClose}
    >
      {/* Backdrop */}
      <Pressable style={styles.backdrop} onPress={handleClose} />

      {/* Bottom sheet */}
      <View style={styles.sheet}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Select parking</Text>
          <Pressable onPress={handleClose} hitSlop={10}>
            <Text style={styles.close}>Close</Text>
          </Pressable>
        </View>

        {/* Search input */}
        <View style={styles.searchWrap}>
          <TextInput
            value={query}
            onChangeText={setQuery}
            placeholder="Search by name or code…"
            placeholderTextColor="#9CA3AF"
            style={styles.searchInput}
            autoCapitalize="none"
            autoCorrect={false}
            returnKeyType="search"
            clearButtonMode="while-editing" // iOS
          />
        </View>

        {/* Recently used */}
        {recentLots.length > 0 && !q ? (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Recently used</Text>
            <View style={{ marginTop: 8 }}>
              {recentLots.map((lot) => {
                const isSelected = lot.code === selectedCode;
                return (
                  <Pressable
                    key={lot.code}
                    onPress={() => handleSelect(lot.code)}
                    style={[styles.recentPill, isSelected && styles.recentPillSelected]}
                  >
                    <Text style={[styles.recentText, isSelected && styles.recentTextSelected]}>
                      {lot.name} ({lot.code})
                    </Text>
                  </Pressable>
                );
              })}
            </View>
          </View>
        ) : null}

        {/* Results */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            {q ? `Results (${filtered.length})` : "All parking lots"}
          </Text>

          <View style={{ marginTop: 8, flex: 1 }}>
            {filtered.length === 0 ? (
              <Text style={{ opacity: 0.7, paddingVertical: 10 }}>
                No matches for “{query}”.
              </Text>
            ) : (
              <FlatList
                data={filtered}
                keyExtractor={(item) => item.code}
                ItemSeparatorComponent={() => <View style={styles.separator} />}
                keyboardShouldPersistTaps="handled"
                renderItem={renderLotItem}
              />
            )}
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.35)",
  },
  sheet: {
    position: "absolute",
    left: 0,
    right: 0,
    bottom: 0,
    maxHeight: "78%",
    backgroundColor: "white",
    borderTopLeftRadius: 18,
    borderTopRightRadius: 18,
    paddingHorizontal: 16,
    paddingTop: 14,
    paddingBottom: 18,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingBottom: 10,
  },
  title: {
    fontSize: 18,
    fontWeight: "700",
  },
  close: {
    fontSize: 14,
    fontWeight: "600",
    opacity: 0.8,
  },
  searchWrap: {
    marginBottom: 12,
  },
  searchInput: {
    borderWidth: 1,
    borderColor: "#E5E7EB",
    borderRadius: 14,
    paddingHorizontal: 12,
    paddingVertical: Platform.OS === "ios" ? 12 : 10,
    fontSize: 15,
    backgroundColor: "#F9FAFB",
  },
  section: {
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: "700",
    opacity: 0.75,
  },
  separator: {
    height: 1,
    backgroundColor: "#eee",
  },
  item: {
    paddingVertical: 14,
    paddingHorizontal: 10,
    borderRadius: 12,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  itemSelected: {
    backgroundColor: "#EEF2FF",
  },
  itemTitle: {
    fontSize: 16,
    fontWeight: "600",
  },
  itemTitleSelected: {
    color: "#1D4ED8",
  },
  itemSubtitle: {
    marginTop: 2,
    fontSize: 13,
    opacity: 0.7,
  },
  itemSubtitleSelected: {
    opacity: 0.9,
  },
  check: {
    fontSize: 18,
    fontWeight: "800",
    color: "#1D4ED8",
  },
  recentPill: {
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: "#E5E7EB",
    marginBottom: 8,
  },
  recentPillSelected: {
    backgroundColor: "#EEF2FF",
    borderColor: "#C7D2FE",
  },
  recentText: {
    fontSize: 14,
    fontWeight: "600",
  },
  recentTextSelected: {
    color: "#1D4ED8",
  },
});
