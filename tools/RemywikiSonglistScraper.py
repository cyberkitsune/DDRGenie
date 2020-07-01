import sys, requests
import wikitextparser as wtp

base_uri = 'https://remywiki.com'
query = '/api.php?action=query&prop=revisions&titles=%s&formatversion=2&redirects=1&rvprop=content&rvslots=*&format=json'

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: RemywikiSonglistScraper.py [Page_Name]")
        exit(1)

    page = sys.argv[1]
    page = page.replace(' ','_')
    print(page)
    final_uri = "%s%s" % (base_uri, query % page)

    r = requests.get(final_uri)
    if r.status_code != 200:
        print("Failure getting URI...")
        exit(1)

    j = r.json()
    content = j['query']['pages'][0]['revisions'][0]['slots']['main']['content']

    songs = []

    parsed = wtp.parse(content)
    lists = parsed.get_lists()
    for list in lists:
        for item in list.items:
            # Weird hack to make sure we're the only newline in town
            songs.append("%s\n" % wtp.remove_markup(item).strip('\n').lstrip())

    with open("%s.txt" % page, 'w', encoding='utf-8') as f:
        f.writelines(songs)

    print("Output: ", "%s.txt" % page)
