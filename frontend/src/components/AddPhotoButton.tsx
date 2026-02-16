import React, { useState } from "react"
import { Button } from "@mui/material"
import BulkUploadModal from "./BulkUploadModal"

interface AddPhotoButtonProps {
    albumId: string
}

export default function AddPhotoButton({ albumId }: AddPhotoButtonProps) {
    const [modalIsOpen, setModalIsOpen] = useState(false)

    return (
        <>
            <Button variant="contained" onClick={() => setModalIsOpen(true)}>
                Ajouter des photos
            </Button>

            <BulkUploadModal
                open={modalIsOpen}
                onClose={() => setModalIsOpen(false)}
                albumId={albumId}
            />
        </>
    )
}
