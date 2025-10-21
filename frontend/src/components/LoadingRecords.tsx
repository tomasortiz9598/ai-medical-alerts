import { useEffect, useMemo, useRef, useState } from "react";
import { Box, Fade, LinearProgress, Paper, Typography } from "@mui/material";
import puppyGif from "../assets/wired-lineal-56-document-hover-swipe.gif";

const messages = [
  "Fetching the latest tail-wagging updates…",
  "Warming up the paw printer for your documents…",
  "Our resident pup is double-checking every page…",
  "Almost there—treats are motivating the review team…",
  "Lining up the leashes, your file is nearly ready…",
];

const MESSAGE_INTERVAL = 4000;
const FADE_DURATION = 350;

export default function LoadingRecords() {
  const [messageIndex, setMessageIndex] = useState(0);
  const [visible, setVisible] = useState(true);
  const timeoutRef = useRef<number | null>(null);

  useEffect(() => {
    const interval = window.setInterval(() => {
      setVisible(false);
      if (timeoutRef.current) {
        window.clearTimeout(timeoutRef.current);
      }
      timeoutRef.current = window.setTimeout(() => {
        setMessageIndex((prev) => (prev + 1) % messages.length);
        setVisible(true);
      }, FADE_DURATION);
    }, MESSAGE_INTERVAL);

    return () => {
      window.clearInterval(interval);
      if (timeoutRef.current) {
        window.clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const message = useMemo(() => messages[messageIndex], [messageIndex]);

  return (
    <Box
      role="status"
      aria-live="polite"
      sx={{
        position: "fixed",
        inset: 0,
        zIndex: (theme) => theme.zIndex.modal + 2,
        display: "flex",
        flexDirection: "column",
        backgroundColor: "rgba(31, 41, 55, 0.75)",
        backdropFilter: "blur(4px)",
        color: "common.white",
      }}
    >
      <LinearProgress
        color="secondary"
        sx={{
          height: 4,
          "& .MuiLinearProgress-bar": {
            animationDuration: "1.6s",
          },
        }}
      />
      <Box
        sx={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          px: 3,
          textAlign: "center",
        }}
      >
        <Paper
          elevation={6}
          sx={{
            p: { xs: 4, sm: 6 },
            maxWidth: 440,
            width: "100%",
            borderRadius: 4,
            background:
              "linear-gradient(135deg, rgba(255,255,255,0.92), rgba(244,246,248,0.95))",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 3,
            boxShadow: "0 18px 38px rgba(15, 23, 42, 0.35)",
          }}
        >
          <Box
            component="img"
            src={puppyGif}
            alt="Animated puppy reviewing documents"
            sx={{
              width: 120,
              height: 120,
              objectFit: "contain",
              filter: "drop-shadow(0 12px 18px rgba(20,110,180,0.35))",
              animation: "float 2.4s ease-in-out infinite",
            }}
          />
          <Fade in={visible} timeout={FADE_DURATION} key={messageIndex}>
            <Typography
              variant="h6"
              sx={{
                fontFamily: "inherit",
                fontWeight: 600,
                color: "text.primary",
              }}
            >
              {message}
            </Typography>
          </Fade>
          <Typography variant="body2" sx={{ color: "text.secondary", fontFamily: "inherit" }}>
            Feel free to stretch—your upload is syncing securely with the care team; just keep this window open so we can finish up smoothly.
          </Typography>
        </Paper>
      </Box>
      <style>{`
        @keyframes float {
          0% { transform: translateY(0px) rotate(-2deg); }
          50% { transform: translateY(-6px) rotate(4deg); }
          100% { transform: translateY(0px) rotate(-2deg); }
        }
      `}</style>
    </Box>
  );
}
