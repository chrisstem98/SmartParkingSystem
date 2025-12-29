import AsyncStorage from "@react-native-async-storage/async-storage";
import * as Crypto from "expo-crypto";

const KEY = "SMARTPARKING_DEVICE_ID";

// Get stable device id (persisted). Create once if missing.
export async function getDeviceId(): Promise<string> {
  const existing = await AsyncStorage.getItem(KEY);
  if (existing) return existing;

  const newId = Crypto.randomUUID();
  await AsyncStorage.setItem(KEY, newId);
  return newId;
}
