import { useCallback, useContext, useEffect, useRef, useState } from "react";
import type { ChangeEvent, MouseEvent } from "react";
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Checkbox,
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
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import InsertDriveFileIcon from "@mui/icons-material/InsertDriveFile";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import { format } from "../utils/dates";
import { ApiContext } from "../context/ApiContext";
import type { FiltersState, MedicalRecord } from "../types";
import { showSnackbar } from "../utils/snackbar";

interface MedicalRecordsCardProps {
  selectedMedicalRecordIds: string[];
  onFiltersChange: (updater: (prev: FiltersState) => FiltersState) => void;
  onResetFilters: () => void;
  onPendingStart: (options?: { showOverlay?: boolean }) => void;
  onPendingEnd: () => void;
  disabled: boolean;
  onAfterChange: () => void;
}

export default function MedicalRecordsCard({
  selectedMedicalRecordIds,
  onFiltersChange,
  onResetFilters,
  onPendingStart,
  onPendingEnd,
  disabled,
  onAfterChange,
}: MedicalRecordsCardProps) {
  const { medicalRecords: medicalRecordsService } = useContext(ApiContext);
  const [records, setRecords] = useState<MedicalRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [menuAnchorEl, setMenuAnchorEl] = useState<HTMLElement | null>(null);
  const [menuRecord, setMenuRecord] = useState<MedicalRecord | null>(null);

  const isMenuOpen = Boolean(menuAnchorEl);
  const menuId = menuRecord ? `medical-record-actions-${menuRecord.id}` : undefined;

  const loadMedicalRecords = useCallback(async () => {
    setLoading(true);
    try {
      const fetchedRecords = await medicalRecordsService.list();
      setRecords(fetchedRecords);
    } catch (error) {
      console.error(error);
      showSnackbar((error as Error).message, "error");
    } finally {
      setLoading(false);
    }
  }, [medicalRecordsService]);

  const hasLoadedRef = useRef(false);

  useEffect(() => {
    if (hasLoadedRef.current) return;
    hasLoadedRef.current = true;
    void loadMedicalRecords();
  }, [loadMedicalRecords]);

  const handleUpload = useCallback(
    async (file: File) => {
      onPendingStart({ showOverlay: true });
      try {
        await medicalRecordsService.upload(file);
        showSnackbar("Patient file uploaded successfully");
        onResetFilters();
        await loadMedicalRecords();
        onAfterChange();
      } catch (error) {
        console.error(error);
        showSnackbar((error as Error).message, "error");
      } finally {
        onPendingEnd();
      }
    },
    [loadMedicalRecords, medicalRecordsService, onPendingEnd, onPendingStart, onResetFilters, onAfterChange]
  );

  const handleDelete = useCallback(
    async (id: string) => {
      onPendingStart();
      try {
        await medicalRecordsService.remove(id);
        showSnackbar("Patient file deleted");
        onResetFilters();
        await loadMedicalRecords();
        onAfterChange();
      } catch (error) {
        console.error(error);
        showSnackbar((error as Error).message, "error");
      } finally {
        onPendingEnd();
      }
    },
    [loadMedicalRecords, medicalRecordsService, onPendingEnd, onPendingStart, onResetFilters, onAfterChange]
  );

  const handleMenuOpen = useCallback(
    (event: MouseEvent<HTMLButtonElement>, record: MedicalRecord) => {
      setMenuAnchorEl(event.currentTarget);
      setMenuRecord(record);
    },
    []
  );

  const handleMenuClose = useCallback(() => {
    setMenuAnchorEl(null);
    setMenuRecord(null);
  }, []);

  const handleMenuDelete = useCallback(() => {
    if (!menuRecord) return;
    handleMenuClose();
    void handleDelete(menuRecord.id);
  }, [handleDelete, handleMenuClose, menuRecord]);

  const handleToggleMedicalRecord = useCallback(
    (id: string) => {
      if (disabled) return;
      onFiltersChange((prev) => {
        const exists = prev.medicalRecordIds.includes(id);
        const medicalRecordIds = exists
          ? prev.medicalRecordIds.filter((value) => value !== id)
          : [...prev.medicalRecordIds, id];
        return { ...prev, medicalRecordIds, page: 1 };
      });
    },
    [disabled, onFiltersChange]
  );

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files?.[0] || disabled) return;
    await handleUpload(event.target.files[0]);
    event.target.value = "";
  };

  return (
    <Card elevation={0} sx={{ height: "100%" }}>
      <CardHeader
        title="Patient files"
        action={
          <>
            <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf"
                style={{ display: "none" }}
                onChange={handleFileChange}
              />
              <IconButton
                color="primary"
                onClick={() => fileInputRef.current?.click()}
                disabled={disabled}
              >
                <AddIcon />
              </IconButton>
          </>
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
              <Skeleton key={key} variant="rounded" height={28} sx={{ mb: 1, borderRadius: 1 }} />
            ))}
          </Box>
        ) : (
          <List dense>
            {records.map((record) => {
              const checked = selectedMedicalRecordIds.includes(record.id);
              return (
                <ListItem key={record.id} disableGutters>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <Checkbox
                      edge="start"
                      checked={checked}
                      disabled={disabled}
                      onChange={() => handleToggleMedicalRecord(record.id)}
                      inputProps={{ "aria-label": `Select ${record.filename}` }}
                    />
                  </ListItemIcon>
                  <InsertDriveFileIcon color="primary" sx={{ mr: 1 }} />
                  <ListItemText
                    primary={record.filename}
                    secondary={`Uploaded ${format(record.created_time)}`}
                    primaryTypographyProps={{
                      noWrap: true,
                      sx: {
                        fontFamily: "inherit",
                        fontWeight: 500,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                      },
                    }}
                    secondaryTypographyProps={{
                      sx: { fontFamily: "inherit", display: "block" },
                    }}
                  />
                  <ListItemSecondaryAction>

                      <IconButton
                        edge="end"
                        aria-label="Open patient file actions"
                        aria-controls={menuRecord?.id === record.id ? menuId : undefined}
                        aria-haspopup="true"
                        onClick={(event) => handleMenuOpen(event, record)}
                        disabled={disabled}
                      >
                        <MoreVertIcon />
                      </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              );
            })}
            {!records.length && (
              <Typography variant="body2" sx={{ fontFamily: "inherit" }} color="text.secondary">
                No patient files uploaded yet.
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
  );
}
