import React, { useState, useEffect } from "react"
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Stack,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Snackbar,
    Alert,
} from "@mui/material"
import { Photo } from "../types/photo"
import { useUpdatePhotoMutation } from "../queries/photos"
import { useAlbums } from "../queries/albums"

interface EditPhotoModalProps {
    open: boolean
    onClose: () => void
    photo: Photo
    albumId: string
}

const EditPhotoModal = ({ open, onClose, photo, albumId }: EditPhotoModalProps) => {
    const [caption, setCaption] = useState(photo.caption || "")
    const [location, setLocation] = useState(photo.location || "")
    const [selectedAlbumId, setSelectedAlbumId] = useState<number>(Number(albumId))
    const [snackbar, setSnackbar] = useState<{
        open: boolean
        message: string
        severity: "success" | "error"
    }>({ open: false, message: "", severity: "success" })

    const updatePhotoMutation = useUpdatePhotoMutation()
    const { data: albums } = useAlbums()

    // Sync state when photo prop changes
    useEffect(() => {
        setCaption(photo.caption || "")
        setLocation(photo.location || "")
        setSelectedAlbumId(Number(albumId))
    }, [photo, albumId])

    const handleSubmit = () => {
        const data: Record<string, unknown> = {}

        if (caption !== (photo.caption || "")) {
            data.caption = caption
        }
        if (location !== (photo.location || "")) {
            data.location = location
        }
        if (selectedAlbumId !== Number(albumId)) {
            data.target_album_id = selectedAlbumId
        }

        if (Object.keys(data).length === 0) {
            onClose()
            return
        }

        updatePhotoMutation.mutate(
            {
                albumId,
                photoId: photo.id,
                data: data as { caption?: string; location?: string; target_album_id?: number },
            },
            {
                onSuccess: () => {
                    setSnackbar({
                        open: true,
                        message: "Photo mise à jour",
                        severity: "success",
                    })
                    onClose()
                },
                onError: () => {
                    setSnackbar({
                        open: true,
                        message: "Erreur lors de la mise à jour",
                        severity: "error",
                    })
                },
            }
        )
    }

    return (
        <>
            <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
                <DialogTitle>Modifier la photo</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{ mt: 1 }}>
                        <TextField
                            label="Légende"
                            value={caption}
                            onChange={(e) => setCaption(e.target.value)}
                            fullWidth
                        />
                        <TextField
                            label="Lieu"
                            value={location}
                            onChange={(e) => setLocation(e.target.value)}
                            fullWidth
                        />
                        {albums && albums.length > 1 && (
                            <FormControl fullWidth>
                                <InputLabel>Album</InputLabel>
                                <Select
                                    value={selectedAlbumId}
                                    label="Album"
                                    onChange={(e) => setSelectedAlbumId(Number(e.target.value))}
                                >
                                    {albums.map((album) => (
                                        <MenuItem key={album.id} value={album.id}>
                                            {album.title}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        )}
                    </Stack>
                </DialogContent>
                <DialogActions>
                    <Button onClick={onClose}>Annuler</Button>
                    <Button
                        onClick={handleSubmit}
                        variant="contained"
                        disabled={updatePhotoMutation.isPending}
                    >
                        Enregistrer
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

export default EditPhotoModal
