import React, { useState, useCallback, useRef } from "react"
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Typography,
    Box,
    IconButton,
    LinearProgress,
    Stack,
    ImageList,
    ImageListItem,
    ImageListItemBar,
    Snackbar,
    Alert,
} from "@mui/material"
import CloseIcon from "@mui/icons-material/Close"
import CloudUploadIcon from "@mui/icons-material/CloudUpload"
import { useAddPhotoMutation } from "../queries/photos"

interface FileEntry {
    file: File
    preview: string
    caption: string
    location: string
    useGlobal: boolean
}

interface BulkUploadModalProps {
    open: boolean
    onClose: () => void
    albumId: string
}

const MAX_CONCURRENT = 3

const BulkUploadModal = ({ open, onClose, albumId }: BulkUploadModalProps) => {
    const [files, setFiles] = useState<FileEntry[]>([])
    const [globalCaption, setGlobalCaption] = useState("")
    const [globalLocation, setGlobalLocation] = useState("")
    const [uploading, setUploading] = useState(false)
    const [progress, setProgress] = useState({ done: 0, total: 0 })
    const [snackbar, setSnackbar] = useState<{
        open: boolean
        message: string
        severity: "success" | "error"
    }>({ open: false, message: "", severity: "success" })
    const fileInputRef = useRef<HTMLInputElement>(null)
    const addPhotoMutation = useAddPhotoMutation()
    const [isDragOver, setIsDragOver] = useState(false)

    const addFiles = useCallback((newFiles: FileList | File[]) => {
        const entries: FileEntry[] = Array.from(newFiles)
            .filter((f) => f.type.startsWith("image/"))
            .map((file) => ({
                file,
                preview: URL.createObjectURL(file),
                caption: "",
                location: "",
                useGlobal: true,
            }))
        setFiles((prev) => [...prev, ...entries])
    }, [])

    const handleDrop = useCallback(
        (e: React.DragEvent) => {
            e.preventDefault()
            setIsDragOver(false)
            if (e.dataTransfer.files.length > 0) {
                addFiles(e.dataTransfer.files)
            }
        },
        [addFiles]
    )

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragOver(true)
    }, [])

    const handleDragLeave = useCallback(() => {
        setIsDragOver(false)
    }, [])

    const removeFile = (index: number) => {
        setFiles((prev) => {
            const copy = [...prev]
            URL.revokeObjectURL(copy[index].preview)
            copy.splice(index, 1)
            return copy
        })
    }

    const updateFileField = (index: number, field: "caption" | "location", value: string) => {
        setFiles((prev) => {
            const copy = [...prev]
            copy[index] = { ...copy[index], [field]: value, useGlobal: false }
            return copy
        })
    }

    const handleUpload = async () => {
        if (files.length === 0) return
        setUploading(true)
        setProgress({ done: 0, total: files.length })

        let successCount = 0
        let errorCount = 0

        // Process in batches with concurrency limit
        const queue = [...files]
        const runBatch = async () => {
            const promises: Promise<void>[] = []
            while (queue.length > 0 && promises.length < MAX_CONCURRENT) {
                const entry = queue.shift()!
                const caption = entry.useGlobal && !entry.caption ? globalCaption : entry.caption
                const location =
                    entry.useGlobal && !entry.location ? globalLocation : entry.location

                const p = addPhotoMutation
                    .mutateAsync({
                        albumId,
                        image: entry.file,
                        caption: caption || undefined,
                        location: location || undefined,
                    })
                    .then(() => {
                        successCount++
                    })
                    .catch(() => {
                        errorCount++
                    })
                    .finally(() => {
                        setProgress((prev) => ({ ...prev, done: prev.done + 1 }))
                    })
                promises.push(p)
            }
            await Promise.all(promises)
            if (queue.length > 0) {
                await runBatch()
            }
        }

        await runBatch()

        setUploading(false)

        if (errorCount > 0) {
            setSnackbar({
                open: true,
                message: `${successCount} photo(s) uploadée(s), ${errorCount} erreur(s)`,
                severity: "error",
            })
        } else {
            setSnackbar({
                open: true,
                message: `${successCount} photo(s) uploadée(s) avec succès`,
                severity: "success",
            })
        }

        // Clean up previews and close
        files.forEach((f) => URL.revokeObjectURL(f.preview))
        setFiles([])
        setGlobalCaption("")
        setGlobalLocation("")
        setProgress({ done: 0, total: 0 })
        onClose()
    }

    const handleClose = () => {
        if (uploading) return
        files.forEach((f) => URL.revokeObjectURL(f.preview))
        setFiles([])
        setGlobalCaption("")
        setGlobalLocation("")
        onClose()
    }

    const progressPercent =
        progress.total > 0 ? Math.round((progress.done / progress.total) * 100) : 0

    return (
        <>
            <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
                <DialogTitle>Ajouter des photos</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{ mt: 1 }}>
                        {/* Drop zone */}
                        <Box
                            onDrop={handleDrop}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onClick={() => fileInputRef.current?.click()}
                            sx={{
                                border: "2px dashed",
                                borderColor: isDragOver ? "primary.main" : "grey.400",
                                borderRadius: 2,
                                p: 4,
                                textAlign: "center",
                                cursor: "pointer",
                                backgroundColor: isDragOver ? "action.hover" : "transparent",
                                transition: "all 0.2s",
                            }}
                        >
                            <CloudUploadIcon sx={{ fontSize: 48, color: "grey.500", mb: 1 }} />
                            <Typography color="text.secondary">
                                Glissez-déposez vos images ici ou cliquez pour parcourir
                            </Typography>
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*"
                                multiple
                                hidden
                                onChange={(e) => {
                                    if (e.target.files) addFiles(e.target.files)
                                    e.target.value = ""
                                }}
                            />
                        </Box>

                        {/* Global fields */}
                        {files.length > 0 && (
                            <Box
                                sx={{
                                    p: 2,
                                    border: "1px solid",
                                    borderColor: "grey.300",
                                    borderRadius: 1,
                                }}
                            >
                                <Typography variant="subtitle2" gutterBottom>
                                    Appliquer à toutes les photos
                                </Typography>
                                <Stack direction="row" spacing={2}>
                                    <TextField
                                        label="Légende commune"
                                        value={globalCaption}
                                        onChange={(e) => setGlobalCaption(e.target.value)}
                                        size="small"
                                        fullWidth
                                    />
                                    <TextField
                                        label="Lieu commun"
                                        value={globalLocation}
                                        onChange={(e) => setGlobalLocation(e.target.value)}
                                        size="small"
                                        fullWidth
                                    />
                                </Stack>
                            </Box>
                        )}

                        {/* Preview grid with per-image overrides */}
                        {files.length > 0 && (
                            <ImageList cols={3} gap={12} sx={{ maxHeight: 400 }}>
                                {files.map((entry, index) => (
                                    <ImageListItem
                                        key={`${entry.file.name}-${index}`}
                                        sx={{
                                            borderRadius: 1,
                                            overflow: "hidden",
                                            border: "1px solid",
                                            borderColor: "grey.200",
                                        }}
                                    >
                                        <img
                                            src={entry.preview}
                                            alt={entry.file.name}
                                            loading="lazy"
                                            style={{
                                                height: 140,
                                                objectFit: "cover",
                                            }}
                                        />
                                        <ImageListItemBar
                                            position="top"
                                            actionPosition="right"
                                            actionIcon={
                                                <IconButton
                                                    size="small"
                                                    onClick={() => removeFile(index)}
                                                    sx={{ color: "white" }}
                                                >
                                                    <CloseIcon fontSize="small" />
                                                </IconButton>
                                            }
                                            sx={{
                                                background:
                                                    "linear-gradient(to bottom, rgba(0,0,0,0.5), transparent)",
                                            }}
                                        />
                                        <Box sx={{ p: 1 }}>
                                            <TextField
                                                placeholder={
                                                    globalCaption || "Légende individuelle"
                                                }
                                                value={entry.caption}
                                                onChange={(e) =>
                                                    updateFileField(
                                                        index,
                                                        "caption",
                                                        e.target.value
                                                    )
                                                }
                                                size="small"
                                                fullWidth
                                                variant="standard"
                                                sx={{ mb: 0.5 }}
                                            />
                                            <TextField
                                                placeholder={globalLocation || "Lieu individuel"}
                                                value={entry.location}
                                                onChange={(e) =>
                                                    updateFileField(
                                                        index,
                                                        "location",
                                                        e.target.value
                                                    )
                                                }
                                                size="small"
                                                fullWidth
                                                variant="standard"
                                            />
                                        </Box>
                                    </ImageListItem>
                                ))}
                            </ImageList>
                        )}

                        {/* Progress bar */}
                        {uploading && (
                            <Box>
                                <LinearProgress
                                    variant="determinate"
                                    value={progressPercent}
                                    sx={{ height: 8, borderRadius: 1 }}
                                />
                                <Typography
                                    variant="caption"
                                    color="text.secondary"
                                    sx={{ mt: 0.5 }}
                                >
                                    {progress.done} / {progress.total} ({progressPercent}%)
                                </Typography>
                            </Box>
                        )}
                    </Stack>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} disabled={uploading}>
                        Annuler
                    </Button>
                    <Button
                        onClick={handleUpload}
                        variant="contained"
                        disabled={files.length === 0 || uploading}
                    >
                        {uploading
                            ? `Upload en cours...`
                            : `Uploader ${files.length} photo${files.length !== 1 ? "s" : ""}`}
                    </Button>
                </DialogActions>
            </Dialog>

            <Snackbar
                open={snackbar.open}
                autoHideDuration={4000}
                onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}
                anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
            >
                <Alert
                    onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}
                    severity={snackbar.severity}
                    variant="filled"
                >
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </>
    )
}

export default BulkUploadModal
