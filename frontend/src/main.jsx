import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { ChakraProvider, createSystem, defaultConfig } from "@chakra-ui/react";
import App from "./App.jsx";

const theme = createSystem(defaultConfig, {
  theme: {
    tokens: {
      colors: {
        primary: {
          50: { value: "#e8f5e8" },
          100: { value: "#c3e6c3" },
          200: { value: "#9dd69d" },
          300: { value: "#76c676" },
          400: { value: "#4fb84f" },
          500: { value: "#2d8f2d" },
          600: { value: "#247a24" },
          700: { value: "#1b651b" },
          800: { value: "#125012" },
          900: { value: "#093b09" },
        },
      },
      fonts: {
        body: {
          value:
            "'Noto Sans JP', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        },
        heading: {
          value:
            "'Noto Sans JP', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        },
      },
    },
  },
});

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <ChakraProvider value={theme}>
      <App />
    </ChakraProvider>
  </StrictMode>
);
