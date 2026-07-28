import re

from backend.app.domain.models import (
    CharacterMemory,
    DocumentAnalysis,
    LocationMemory,
    ObjectMemory,
    TimelineEvent,
)


class CharacterMemoryAgent:
    async def run(self, document: DocumentAnalysis) -> list[CharacterMemory]:
        names = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b", "\n".join(document.paragraphs))
        ignored = {document.title, "The", "A", "An", "In", "On", "At", "Scene"}
        unique_names = []
        for name in names:
            if name not in ignored and name not in unique_names:
                unique_names.append(name)

        characters: list[CharacterMemory] = []
        for name in unique_names[:10]:
            characters.append(
                CharacterMemory(
                    name=name,
                    height="175 cm",
                    body_type="athletic build",
                    face_shape="chiseled jawline",
                    eye_colour="expressive dark brown",
                    hair="dark wavy",
                    hairstyle="neat cinematic cut",
                    skin_tone="warm olive",
                    clothing="custom story attire matching time period",
                    voice="confident cinematic tone",
                    power_level="7/10",
                    abilities=["acute observation", "decisive action"],
                )
            )
        return characters


class LocationMemoryAgent:
    async def run(self, document: DocumentAnalysis) -> list[LocationMemory]:
        location_markers = re.findall(
            r"\b(?:in|at|near|inside|outside)\s+([A-Z][A-Za-z' -]{2,40})",
            "\n".join(document.paragraphs),
        )
        names = []
        for marker in location_markers:
            name = marker.strip(" .,;:")
            if name and name not in names:
                names.append(name)
        if not names:
            names = ["Primary Story World"]

        locations: list[LocationMemory] = []
        for name in names[:8]:
            locations.append(
                LocationMemory(
                    name=name,
                    architecture="classic structural design",
                    lighting="dramatic atmospheric lighting",
                    weather="clear with subtle mist",
                    time_of_day="dusk",
                    camera_mood="cinematic suspense",
                    environment="inferred from source narrative",
                    textures="weathered stone and polished wood",
                    vegetation="dense surrounding foliage",
                    props=["lanterns", "carved stone pillars", "ancient manuscripts"],
                    colour_palette="deep cyan and warm amber tones",
                )
            )
        return locations


class ObjectMemoryAgent:
    async def run(self, document: DocumentAnalysis) -> list[ObjectMemory]:
        object_words = ["book", "weapon", "car", "ring", "letter", "door", "house", "ship", "sword", "table"]
        lowered = "\n".join(document.paragraphs).lower()
        return [
            ObjectMemory(name=word, category="story_object", description=f"Mentioned in source narrative as {word}.")
            for word in object_words
            if word in lowered
        ]


class TimelineAgent:
    async def run(self, document: DocumentAnalysis) -> list[TimelineEvent]:
        events: list[TimelineEvent] = []
        for index, paragraph in enumerate(document.paragraphs[:20], start=1):
            events.append(
                TimelineEvent(
                    order=index,
                    label=f"Story beat {index}",
                    summary=paragraph[:240],
                )
            )
        return events
