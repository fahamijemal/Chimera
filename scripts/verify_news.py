from chimera.mcp.servers.news_server import get_latest_news, read_feed

def test_news_fetching():
    print("Testing 'news://latest' resource...")
    try:
        news = get_latest_news()
        print("\n--- Latest News ---")
        print(news)
        print("-------------------\n")
    except Exception as e:
        print(f"FAILED to get latest news: {e}")

    print("Testing 'read_feed' tool (BBC Technology)...")
    try:
        bs_url = "http://feeds.bbci.co.uk/news/technology/rss.xml"
        feed_content = read_feed(bs_url, limit=3)
        print("\n--- BBC Tech Feed ---")
        print(feed_content)
        print("---------------------\n")
    except Exception as e:
         print(f"FAILED to read feed: {e}")

    except Exception as e:
         print(f"FAILED to read feed: {e}")

    print("Testing NewsIngester integration...")
    try:
        from chimera.core.perception import NewsIngester
        ingester = NewsIngester()
        # reusing 'news' from the first test
        if 'news' in locals() and news:
            items = ingester.parse_mcp_news_response(news)
            print(f"Parsed {len(items)} items.")
            if items:
                print(f"Sample Item: {items[0]}")
            print("Integration Test: SUCCESS")
        else:
            print("Skipping integration test (no news data)")
            
    except Exception as e:
        print(f"Integration Test FAILED: {e}")

if __name__ == "__main__":
    test_news_fetching()
