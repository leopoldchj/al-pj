import React from "react"
import { render, screen, fireEvent } from "@testing-library/react"
import "@testing-library/jest-dom"
import SelectAlbumModal from "./SelectAlbumModal"
import { useAlbums } from "../queries/albums"

jest.mock("../queries/albums", () => ({
    useAlbums: jest.fn(),
}))

const mockAlbums = [
    { id: 1, title: "Vacances", description: "", cover_image: "", created_at: "", updated_at: "", nb_photos: 5 },
    { id: 2, title: "Famille", description: "", cover_image: "", created_at: "", updated_at: "", nb_photos: 3 },
    { id: 3, title: "Amis", description: "", cover_image: "", created_at: "", updated_at: "", nb_photos: 0 },
]

describe("SelectAlbumModal", () => {
    const onClose = jest.fn()
    const onSelect = jest.fn()

    beforeEach(() => {
        jest.clearAllMocks()
        ;(useAlbums as jest.Mock).mockReturnValue({ data: mockAlbums, isLoading: false })
    })

    it("renders albums excluding the current album", () => {
        render(
            <SelectAlbumModal
                open={true}
                onClose={onClose}
                onSelect={onSelect}
                currentAlbumId="1"
                title="Déplacer vers..."
            />
        )

        expect(screen.getByText("Famille")).toBeInTheDocument()
        expect(screen.getByText("Amis")).toBeInTheDocument()
        expect(screen.queryByText("Vacances")).not.toBeInTheDocument()
    })

    it("calls onSelect when an album is clicked", () => {
        render(
            <SelectAlbumModal
                open={true}
                onClose={onClose}
                onSelect={onSelect}
                currentAlbumId="1"
                title="Déplacer vers..."
            />
        )

        fireEvent.click(screen.getByText("Famille"))
        expect(onSelect).toHaveBeenCalledWith(mockAlbums[1])
    })

    it("does not render when open is false", () => {
        render(
            <SelectAlbumModal
                open={false}
                onClose={onClose}
                onSelect={onSelect}
                currentAlbumId="1"
                title="Déplacer vers..."
            />
        )

        expect(screen.queryByText("Déplacer vers...")).not.toBeInTheDocument()
    })

    it("displays the title", () => {
        render(
            <SelectAlbumModal
                open={true}
                onClose={onClose}
                onSelect={onSelect}
                currentAlbumId="1"
                title="Copier vers..."
            />
        )

        expect(screen.getByText("Copier vers...")).toBeInTheDocument()
    })

    it("calls onClose when cancel button is clicked", () => {
        render(
            <SelectAlbumModal
                open={true}
                onClose={onClose}
                onSelect={onSelect}
                currentAlbumId="1"
                title="Déplacer vers..."
            />
        )

        fireEvent.click(screen.getByText("Annuler"))
        expect(onClose).toHaveBeenCalled()
    })
})
