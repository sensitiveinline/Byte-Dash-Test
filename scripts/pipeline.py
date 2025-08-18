from scripts.collectors import news_agent, github_agent
from scripts.scorers import platforms_ranker
from scripts.notes import note_agent

if __name__=="__main__":
    news_agent.run()
    github_agent.run()
    platforms_ranker.run()
    note_agent.daily()
    print("✅ pipeline: news/github/platforms/note → data/*.json 완료")
