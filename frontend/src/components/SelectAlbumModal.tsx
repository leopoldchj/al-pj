import React from "react"
import {
    Dialog,
    DialogTitle,
    DialogContent,
    List,
    ListItemButton,
    ListItemText,
    DialogActions,
    Button,
    CircularProgress,
    Typography,
} from "@mui/material"
import { useAlbums } from "../queries/albums"
import { IAlbum } from "../types/album"

interface SelectAlbumModalProps {
    open: boolean
    onClose: () => void
    onSelect: (album: IAlbum) => void
    currentAlbumId: string
    title: string
    loading?: boolean
}

const SelectAlbumModal = ({
    open,
    onClose,
    onSelect,
    currentAlbumId,
    title,
    loading = false,
}: SelectAlbumModalProps) => {
    const { data: albums, isLoading } = useAlbums()

    const filteredAlbums = albums?.filter(
        (album) => String(album.id) !== String(currentAlbumId)
    )

    return (
        <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
            <DialogTitle>{title}</DialogTitle>
            <DialogContent>
                {isLoading || loading ? (
                    <CircularProgress sx={{ display: "block", mx: "auto", my: 2 }} />
                ) : filteredAlbums && filteredAlbums.length > 0 ? (
                    <List>
                        {filteredAlbums.map((album) => (
                            <ListItemButton
                                key={album.id}
                                onClick={() => onSelect(album)}
                                disabled={loading}
                            >
                                <ListItemText
                                    primary={album.title}
                                    secondary={`${album.nb_photos} photo${album.nb_photos !== 1 ? "s" : ""}`}
                                />
                            </ListItemButton>
                        ))}
                    </List>
                ) : (
                    <Typography color="text.secondary" sx={{ py: 2, textAlign: "center" }}>
                        Aucun autre album disponible.
                    </Typography>
                )}
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} disabled={loading}>
                    Annuler
                </Button>
            </DialogActions>
        </Dialog>
    )
}

export default SelectAlbumModal
