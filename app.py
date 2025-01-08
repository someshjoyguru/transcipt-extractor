from pytube import Playlist
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_transcript(video_url):
    video_id = video_url.split("v=")[-1]
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = "\n".join([entry['text'] for entry in transcript])
        print(transcript_text)
        return f"Episode: {video_url}\n\n{transcript_text}\n\n{'=' * 80}\n\n"
    except (TranscriptsDisabled, NoTranscriptFound):
        return f"Episode: {video_url}\n\n[Transcript not available]\n\n{'=' * 80}\n\n"

def extract_playlist_transcripts(playlist_url, output_file="playlist_transcripts.txt"):
    playlist = Playlist(playlist_url)
    print(f"Fetching playlist: {playlist.title}")
    
    video_urls = playlist.video_urls
    print(f"Found {len(video_urls)} videos in the playlist.")
    

    results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(fetch_transcript, url): url for url in video_urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception as e:
                results[url] = f"Episode: {url}\n\n[Error fetching transcript: {e}]\n\n{'=' * 80}\n\n"

    with open(output_file, "w", encoding="utf-8") as file:
        for url in video_urls:
            file.write(results.get(url, f"Episode: {url}\n\n[Transcript not available]\n\n{'=' * 80}\n\n"))
    print(f"Transcripts saved to {output_file}")


if __name__ == "__main__":
    playlist_url = input("Enter the YouTube playlist URL: ")
