import { createTheme } from "@mui/material";

export const theme = createTheme({
  palette: {
    primary: { main: "#146EB4" },
    secondary: { main: "#00A688" },
    background: { default: "#F3F6FA" },
  },
  shape: { borderRadius: 14 },
  typography: {
    fontFamily: `'Inter', 'Roboto', 'Helvetica', 'Arial', sans-serif`,
    h4: {
      fontWeight: 700,
      letterSpacing: "0.01em",
    },
    h6: {
      fontWeight: 600,
      letterSpacing: "0.01em",
    },
    subtitle2: {
      fontWeight: 600,
      letterSpacing: "0.02em",
    },
    body1: {
      letterSpacing: "0.01em",
    },
    body2: {
      letterSpacing: "0.015em",
    },
    caption: {
      letterSpacing: "0.04em",
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        "html, body, #root": {
          height: "100%",
        },
        body: {
          overflow: "hidden",
          backgroundColor: "#F3F6FA",
        },
      },
    },
  },
});
