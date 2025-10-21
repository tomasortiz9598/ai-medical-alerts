import { useCallback, useContext, useEffect, useRef, useState } from "react";
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemSecondaryAction,
  ListItemText,
  Menu,
  MenuItem,
  Skeleton,
  Typography,
  TextField,
  Button,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import { ApiContext } from "../context/ApiContext";
import type { EventType, FiltersState } from "../types";
import { showSnackbar } from "../utils/snackbar";

interface EventTypesCardProps {
  selectedEventTypeIds: string[];
  onFiltersChange: (updater: (prev: FiltersState) => FiltersState) => void;
  onPendingStart: () => void;
  onPendingEnd: () => void;
  disabled: boolean;
}

const defaultForm = { name: "", description: "" };

export default function EventTypesCard({
  selectedEventTypeIds,
  onFiltersChange,
  onPendingStart,
  onPendingEnd,
  disabled,
}: EventTypesCardProps) {
  const { eventTypes: eventTypesService } = useContext(ApiContext);
  const [eventTypes, setEventTypes] = useState<EventType[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState(defaultForm);
  const [menuAnchorEl, setMenuAnchorEl] = useState<HTMLElement | null>(null);
  const [menuEventType, setMenuEventType] = useState<EventType | null>(null);

  const isMenuOpen = Boolean(menuAnchorEl);
  const menuId = menuEventType ? `event-type-actions-${menuEventType.id}` : undefined;

  const loadEventTypes = useCallback(async () => {
    setLoading(true);
    try {
      const data = await eventTypesService.list();
      setEventTypes(data);
    } catch (error) {
      console.error(error);
      showSnackbar((error as Error).message, "error");
    } finally {
      setLoading(false);
    }
  }, [eventTypesService]);

  const hasLoadedRef = useRef(false);

  useEffect(() => {
    if (hasLoadedRef.current) return;
    hasLoadedRef.current = true;
    void loadEventTypes();
  }, [loadEventTypes]);

  const handleOpen = () => {
    if (disabled) return;
    setForm(defaultForm);
    setOpen(true);
  };

  const handleClose = () => setOpen(false);

  const handleChange = (field: keyof typeof defaultForm) =>
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setForm((prev) => ({ ...prev, [field]: event.target.value }));
    };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (disabled) return;
    if (!form.name.trim() || !form.description.trim()) return;
    onPendingStart();
    try {
      await eventTypesService.create({
        name: form.name.trim(),
        description: form.description.trim(),
      });
      showSnackbar("Reminder category added");
      setOpen(false);
      await loadEventTypes();
    } catch (error) {
      console.error(error);
      showSnackbar((error as Error).message, "error");
    } finally {
      onPendingEnd();
    }
  };

  const handleDelete = useCallback(
    async (id: string) => {
      onPendingStart();
      try {
        await eventTypesService.remove(id);
        showSnackbar("Reminder category deleted");
        onFiltersChange((prev) => {
          if (!prev.eventTypeIds.includes(id)) return prev;
          return {
            ...prev,
            eventTypeIds: prev.eventTypeIds.filter((value) => value !== id),
            page: 1,
          };
        });
        await loadEventTypes();
      } catch (error) {
        console.error(error);
        showSnackbar((error as Error).message, "error");
      } finally {
        onPendingEnd();
      }
    },
    [eventTypesService, loadEventTypes, onFiltersChange, onPendingEnd, onPendingStart]
  );

  const handleMenuOpen = useCallback(
    (event: React.MouseEvent<HTMLButtonElement>, eventType: EventType) => {
      setMenuAnchorEl(event.currentTarget);
      setMenuEventType(eventType);
    },
    []
  );

  const handleMenuClose = useCallback(() => {
    setMenuAnchorEl(null);
    setMenuEventType(null);
  }, []);

  const handleMenuDelete = useCallback(() => {
    if (!menuEventType) return;
    handleMenuClose();
    void handleDelete(menuEventType.id);
  }, [handleDelete, handleMenuClose, menuEventType]);

  const handleToggleEventType = useCallback(
    (id: string) => {
      if (disabled) return;
      onFiltersChange((prev) => {
        const exists = prev.eventTypeIds.includes(id);
        const eventTypeIds = exists
          ? prev.eventTypeIds.filter((value) => value !== id)
          : [...prev.eventTypeIds, id];
        return { ...prev, eventTypeIds, page: 1 };
      });
    },
    [disabled, onFiltersChange]
  );

  return (
    <>
      <Card elevation={0} sx={{ height: "100%" }}>
        <CardHeader
          title="Reminder categories"
          action={
                <IconButton color="primary" onClick={handleOpen} disabled={disabled}>
                  <AddIcon />
                </IconButton>
          }
        />
        <CardContent
          sx={{
            pt: 0,
            maxHeight: 300,
            overflowY: "auto",
          }}
        >
          {loading ? (
            <Box>
              {[1, 2, 3, 4].map((key) => (
                <Skeleton
                  key={key}
                  variant="rounded"
                  height={28}
                  sx={{ mb: 1, borderRadius: 1 }}
                />
              ))}
            </Box>
          ) : (
            <List dense>
              {eventTypes.map((type) => {
                const checked = selectedEventTypeIds.includes(type.id);
                return (
                  <ListItem key={type.id} disableGutters>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <Checkbox
                        edge="start"
                        checked={checked}
                        disabled={disabled}
                        onChange={() => handleToggleEventType(type.id)}
                        inputProps={{ "aria-label": `Select ${type.name}` }}
                      />
                    </ListItemIcon>
                    <ListItemText
                      primary={type.name}
                      primaryTypographyProps={{ sx: { fontFamily: "inherit", fontWeight: 500 } }}
                    />
                    {type.is_deletable && (
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          aria-label="Open reminder category actions"
                          aria-controls={menuEventType?.id === type.id ? menuId : undefined}
                          aria-haspopup="true"
                          onClick={(event) => handleMenuOpen(event, type)}
                          disabled={disabled}
                        >
                          <MoreVertIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    )}
                  </ListItem>
                );
              })}
              {!eventTypes.length && (
                <Typography variant="body2" sx={{ fontFamily: "inherit" }} color="text.secondary">
                  No event types available.
                </Typography>
              )}
            </List>
          )}
          <Menu
            id={menuId}
            anchorEl={menuAnchorEl}
            open={isMenuOpen}
            onClose={handleMenuClose}
            anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
            transformOrigin={{ vertical: "top", horizontal: "right" }}
          >
            <MenuItem onClick={handleMenuDelete} disabled={disabled}>
              <ListItemIcon>
                <DeleteIcon fontSize="small" color="error" />
              </ListItemIcon>
              <ListItemText primary="Delete" />
            </MenuItem>
          </Menu>
        </CardContent>
      </Card>

      <Dialog open={open} onClose={disabled ? undefined : handleClose} fullWidth maxWidth="sm">
        <DialogTitle>Add a new reminder category</DialogTitle>
        <Box component="form" onSubmit={handleSubmit}>
          <DialogContent dividers>
            <TextField
              autoFocus
              margin="dense"
              label="Name"
              fullWidth
              value={form.name}
              onChange={handleChange("name")}
              required
              disabled={disabled}
            />
            <TextField
              margin="dense"
              label="Description"
              fullWidth
              multiline
              minRows={2}
              value={form.description}
              onChange={handleChange("description")}
              required
              disabled={disabled}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose} disabled={disabled}>
              Cancel
            </Button>
            <Button type="submit" variant="contained" disabled={disabled}>
              Create
            </Button>
          </DialogActions>
        </Box>
      </Dialog>
    </>
  );
}
