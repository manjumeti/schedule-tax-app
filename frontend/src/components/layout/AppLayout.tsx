import { NavLink, Outlet } from "react-router-dom";
import { AppBar, Box, Chip, Container, Tab, Tabs, Toolbar, Typography } from "@mui/material";
import { useCurrentSession } from "@/context/SessionContext";

const NAV_ITEMS = [
  { label: "Dashboard", path: "/" },
  { label: "Schedule FSI", path: "/fsi" },
  { label: "Form A3", path: "/a3" },
  { label: "Sessions", path: "/sessions" },
];

export function AppLayout() {
  const { sessionId } = useCurrentSession();

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "grey.50" }}>
      <AppBar position="static" color="primary" enableColorOnDark>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            ITR Foreign Income &amp; Assets Filing
          </Typography>
          {sessionId ? (
            <Chip
              size="small"
              color="secondary"
              label={`Session: ${sessionId.slice(0, 8)}`}
              data-testid="active-session-chip"
            />
          ) : (
            <Chip size="small" label="No active session" variant="outlined" />
          )}
        </Toolbar>
        <Tabs
          value={false}
          textColor="inherit"
          indicatorColor="secondary"
          variant="scrollable"
          sx={{ bgcolor: "primary.dark" }}
        >
          {NAV_ITEMS.map((item) => (
            <Tab
              key={item.path}
              label={item.label}
              component={NavLink}
              to={item.path}
              sx={{
                "&.active": { fontWeight: 700, opacity: 1 },
              }}
            />
          ))}
        </Tabs>
      </AppBar>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Outlet />
      </Container>
    </Box>
  );
}
