import re
from typing import Optional, Tuple

def clean_parts(
    filename: str,
    detect_year: bool = False,
    detect_show_info: bool = False
) -> tuple[list[str], int | None, tuple[int, list[int]] | None]:
    """
    Clean filename parts by stripping extensions, splitting, removing junk,
    and optionally detect year and season/episode info.

    Args:
        filename (str): Raw filename.
        detect_year (bool): Whether to look for a year in the parts.
        detect_show_info (bool): Whether to detect season/episode info.

    Returns:
        tuple:
            - cleaned_parts (list[str]): Parts with junk removed.
            - year (int | None): Detected year if any.
            - show_info (tuple[int, list[int]] | None): Detected season and episode(s) if any.
    """
    
    cleaned_parts = []
    year = None
    show_info = None
    junk = {"720p", "1080p", "2160p", "x264", "x265", "h264", "bluray", "webrip", "hdrip"}
    
    name = re.sub(r"(\.[^.]+)+$", "", filename)
    
    if detect_year:
        pattern = re.search(r"(19|20)\d{2}", name)
        if pattern:
            year = int(pattern.group())
    
    if detect_show_info:
        pattern = re.search(
            r"S?(\d{1,2})[xE](\d{2})(?:-?E?(\d{2}))?",
            name, re.IGNORECASE
        )
        if pattern:
            episodes = []
            season = int(pattern.group(1))
            episode = int(pattern.group(2))
            last_episode = pattern.group(3)
            if last_episode:
                episodes.extend(range(episode, int(last_episode) + 1))
            else:
                episodes.append(episode)
            show_info = (season, episodes)
    
    parts = re.split(r"[.\-_\s]", name)
    
    for part in parts:
        token = part.strip("()[]").lower()
        
        if year and token == str(year):
            continue
            
        if token not in junk:
            cleaned_parts.append(token)
            
    return cleaned_parts, year, show_info

def smart_title(text: str) -> str:
    """
        Ignore common small words when applying title-case to filename,
        except when they are at the beginning.
        Example: 'the lord of the rings' -> 'The Lord of the Rings'
    """
    
    SMALL_WORDS = {
        "a", "an", "and", "as", "at", "but", "by", "for",
        "in", "nor", "of", "on", "or", "per", "the", "to", "vs", "via"
    }

    words = text.split()
    titled = []
    for i, word in enumerate(words):
        if i == 0 or word.lower() not in SMALL_WORDS:
            titled.append(word.capitalize())
        else:
            titled.append(word.lower())
    return " ".join(titled)

def parse_movie(filename: str) -> dict:
    """
    Parse a media filename to extract title and year.
    Example: 'The.Matrix.1999.1080p.mkv' -> ('The Matrix', 1999)
    
    Args:
        filename (str): The raw movie filename.
        
    Returns:
        dict:
            - title (str): The cleaned, human-readable movie title.
            - year (int | None): The release year if detected, otherwise None.
    """
    
    cleaned_parts, year, _ = clean_parts(filename, detect_year=True, detect_show_info=False)
    title = smart_title(" ".join(cleaned_parts).strip())
    
    return {"title": title, "year": year}
    
def parse_show(filename: str) -> dict:
    """
    Parse a TV Show filename into structured data.
    
    Args:
        filename (str): The raw TV Show filename.
        
    Returns:
        dict: Parsed info with keys:
            - "title" (str): Show title
            - "season" (int): Season number
            - "episode" (list[int]): Episode number(s)
            - "episode_title" (str | None): Optional episode title
    """
    
    cleaned_parts, _, show_info = clean_parts(filename, detect_year=False, detect_show_info=True)
    
    season = episodes = episode_title = None
    
    token_index = len(cleaned_parts)
    
    if show_info:
        season, episodes = show_info
    
        # Attempt to find the first episode token containing an episode number
        for i, part in enumerate(cleaned_parts):
            if any(str(episode) == part for episode in episodes):
                token_index = i
                break
         
        # Attempt to get the episode title after the last episode token
        last_episode_index = token_index
        for i in range(token_index, len(cleaned_parts)):
            if any(str(episode) == cleaned_parts[i] for episode in episodes):
                last_episode_index = i
            else:
                break
        
        if last_episode_index + 1 < len(cleaned_parts):
            episode_title = smart_title(" ".join(cleaned_parts[last_episode_index + 1:]).strip())
    
    title = smart_title(" ".join(cleaned_parts[:token_index]).strip())

    return {
        "title": title,
        "season": season,
        "episodes": episodes,
        "episode_title": episode_title
    }
