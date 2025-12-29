import React from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import LiveScreen from "../screens/LiveScreen";
import ReservationScreen from "../screens/ReservationScreen";

export type RootTabParamList = {
  Live: undefined;
  Reserve: undefined;
};

const Tab = createBottomTabNavigator<RootTabParamList>();

export default function RootTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: true,
        tabBarHideOnKeyboard: true,
      }}
    >
      <Tab.Screen
        name="Live"
        component={LiveScreen}
        options={{ title: "Live" }}
      />
      <Tab.Screen
        name="Reserve"
        component={ReservationScreen}
        options={{ title: "Reserve" }}
      />
    </Tab.Navigator>
  );
}
