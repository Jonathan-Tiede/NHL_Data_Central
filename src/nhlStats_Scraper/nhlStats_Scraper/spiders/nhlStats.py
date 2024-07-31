import scrapy
from scrapy_playwright.page import PageMethod

# Run scraper by executing: 
# "scrapy crawl NHLStats -o teams.json" in terminal when in dir ../src/nhlStats_Scraper
    # if you don't use "-o teams.json", there will be no .json file created from the run. once spider is working, no need to create this .json file.

class NHLStatsSpider(scrapy.Spider):
    name = "NHL_Season_Stats"

    def start_requests(self):
        global season_ext
        season_ext = '/season/2024/seasontype/2'
        # season_ext = ['/season/2024/seasontype/2', '/season/2023/seasontype/2']

        yield scrapy.Request(f'https://www.espn.com/nhl/stats/team/_{season_ext}', 
                            meta=dict(playwright = True,
                                    playwright_include_page = True,
                                    playwright_page_methods = [PageMethod('wait_for_selector', 'div.page-container.cf')]
                                    ),
                            callback=self.parse
                            )

    async def parse(self, response):
        global season_info
        cnt = 0
        team_data = {}

        season = response.css('h1.headline.headline__h1.dib::Text').get()
        sub1 = 'Skating'
        sub2 = 'Stats'
        idx1 = season.index(sub1)
        idx2 = season.index(sub2)
        season_type = ''
        season_year = ''
        for idx in range(idx1 + len(sub1) + 1, idx2 - 1):
            season_type = season_type + season[idx]
        for idx in range(idx2 + len(sub2) + 1, len(season)):
            season_year = season_year + season[idx]
        season_info = season_year + ' ' + season_type
        team_data['season'] = season_info
        
        teams = response.xpath('//*[@id="fittPageContainer"]/div[3]/div/div/section/div/div[4]/div/table/tbody')
        team_data['teamNames'] = teams.css('a.AnchorLink::Text').getall()
        team_data['teamLinks'] = ['https://www.espn.com' + route for route in teams.css('span a.AnchorLink::attr(href)').getall()]

        headers = response.xpath('//*[@id="fittPageContainer"]/div[3]/div/div/section/div/div[4]/div/div/div[2]/table/thead/tr')
        team_data['colHeader'] = headers.css('div::Text, a::Text').getall()

        stats = response.xpath('//*[@id="fittPageContainer"]/div[3]/div/div/section/div/div[4]/div/div/div[2]/table/tbody/tr')
        team_stats = []
        for stat in stats:
            team_stats.append(stat.css('div::Text').getall())
        team_data['teamStats'] = team_stats

        URL = team_data['teamLinks'][cnt]
        URL = URL.replace('team/', 'team/stats/')
        URL = URL.split("/")
        URL = '/'.join([URL[0], URL[1], URL[2], URL[3], URL[4], URL[5], URL[6], URL[7], URL[8]])
        URL = URL+season_ext

        # ------------------------------------
        # This will be replaced with call to database to store data.
        yield team_data
        # ------------------------------------

        yield response.follow(URL,
                              callback=self.parse_skater_by_team,
                              meta={
                                  'teamLinks':team_data['teamLinks'],
                                  'teamCount':cnt
                                  })
        

    async def parse_skater_by_team(self, response):

        num_teams = len(response.meta['teamLinks'])
        cnt = response.meta['teamCount']

        player_data = {}

        '''
        Skaters
        '''
        players = response.xpath('//*[@id="fittPageContainer"]/div[2]/div[5]/div/div/section/div/div[7]/div[2]/table/tbody')
        player_data['team'] = response.css('span.db.pr3.nowrap::Text').get() + ' ' + response.css('span.db.fw-bold::Text').get()
        player_data['playerNames'] = players.css('a.AnchorLink::Text').getall()
        player_data['playerPos'] = players.css('span.font10::Text').getall()
        player_data['playerPos'] = [pos for pos in player_data['playerPos'] if pos != ' ']
        player_data['playerLinks'] = players.css('a.AnchorLink::attr(href)').getall()

        player_data['season'] = season_info

        headers = response.xpath('//*[@id="fittPageContainer"]/div[2]/div[5]/div/div/section/div/div[7]/div[2]/div/div[2]/table/thead/tr')
        player_data['colHeader'] = headers.css('a::Text').getall()

        stats = response.xpath('//*[@id="fittPageContainer"]/div[2]/div[5]/div/div/section/div/div[7]/div[2]/div/div[2]/table/tbody/tr')
        team_stats = []
        for stat in stats:
            team_stats.append(stat.css('span::Text').getall())
        player_data['playerStats'] = team_stats

        # ------------------------------------
        # This will be replaced with call to database to store data.
        yield player_data
        # ------------------------------------

        if cnt <= num_teams-1:
            URL = response.meta['teamLinks'][cnt]
            URL = URL.replace('team/', 'team/stats/')
            URL = URL.replace('name/', 'type/goalie/name/')
            URL = URL.split("/")
            URL = '/'.join([URL[0], URL[1], URL[2], URL[3], URL[4], URL[5], URL[6], URL[7], URL[8], URL[9], URL[10]])
            URL = URL+season_ext
            yield response.follow(URL,
                                  callback=self.parse_goalie_by_team,
                                  meta={'teamLinks':response.meta['teamLinks'],
                                        'teamCount':cnt
                                        })
    

    async def parse_goalie_by_team(self, response):

        num_teams = len(response.meta['teamLinks'])        
        cnt = response.meta['teamCount']

        player_data = {}

        '''
        Goalies
        '''
        players = response.xpath('//*[@id="fittPageContainer"]/div[2]/div[5]/div/div/section/div/div[4]/div[2]/table/tbody')
        player_data['team'] = response.css('span.db.pr3.nowrap::Text').get() + ' ' + response.css('span.db.fw-bold::Text').get()
        player_data['playerNames'] = players.css('a.AnchorLink::Text').getall()
        player_data['playerPos'] = players.css('span.font10::Text').getall()
        player_data['playerPos'] = [pos for pos in player_data['playerPos'] if pos != ' ']
        player_data['playerLinks'] = players.css('a.AnchorLink::attr(href)').getall()

        player_data['season'] = season_info

        headers = response.xpath('//*[@id="fittPageContainer"]/div[2]/div[5]/div/div/section/div/div[4]/div[2]/div/div[2]/table/thead/tr')
        player_data['colHeader'] = headers.css('a::Text').getall()

        stats = response.xpath('//*[@id="fittPageContainer"]/div[2]/div[5]/div/div/section/div/div[4]/div[2]/div/div[2]/table/tbody/tr')
        team_stats = []
        for stat in stats:
            team_stats.append(stat.css('span::Text').getall())
        player_data['playerStats'] = team_stats

        # ------------------------------------
        # This will be replaced with call to database to store data.
        yield player_data
        # ------------------------------------

        if cnt < num_teams-1:
            cnt += 1
            URL = response.meta['teamLinks'][cnt]
            URL = URL.replace('team/', 'team/stats/')
            URL = URL.split("/")
            URL = '/'.join([URL[0], URL[1], URL[2], URL[3], URL[4], URL[5], URL[6], URL[7], URL[8]])
            URL = URL+season_ext
            yield response.follow(URL,
                                    callback=self.parse_skater_by_team,
                                    meta={'teamLinks':response.meta['teamLinks'],
                                        'teamCount':cnt
                                        })
        else:
            pass