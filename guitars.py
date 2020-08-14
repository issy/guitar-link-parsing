import aiohttp
import discord
from discord.ext import commands
import bs4
from bs4 import BeautifulSoup as Soup

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}

class Guitar(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Guitar cog online')

    @commands.Cog.listener()
    async def on_message(self, message):
        # we do not want the bot to reply to itself or other bots
        if message.author.bot == True or message.author.id == self.client.user.id:
            return

        if 'https://www.andertons.co.uk/guitar-dept/' in message.content.lower():
            for word in message.content.lower().split(' '):
                if not word.startswith('https://www.andertons.co.uk/guitar-dept/') or len(word) <= 57:
                    continue
                productData = await self.get_andertons_data(word)
                if productData is None:
                    continue
                newEmbed = await self.make_guitar_embed(productData)
                await message.edit(suppress=True)
                await message.channel.send(embed=newEmbed)
        if 'https://www.pmtonline.co.uk/' in message.content.lower():
            for word in message.content.lower().split(' '):
                if not word.startswith('https://www.pmtonline.co.uk/') or len(word) <= 28:
                    continue
                productData = await self.get_pmt_data(word)
                if productData is None:
                    continue
                newEmbed = await self.make_guitar_embed(productData)
                await message.edit(suppress=True)
                await message.channel.send(embed=newEmbed)
        if 'https://www.thomann.de/' in message.content.lower():
            for word in message.content.lower().split(' '):
                if not word.startswith('https://www.thomann.de/') or len(word) <= 23:
                    continue
                productData = await self.get_thomann_data(word)
                if productData is None:
                    continue
                newEmbed = await self.make_guitar_embed(productData)
                await message.edit(suppress=True)
                await message.channel.send(embed=newEmbed)

    async def make_guitar_embed(self, guitar):
        embed = discord.Embed()
        embed.set_author(name=guitar['title'],url=guitar['url'])
        embed.set_thumbnail(url=guitar['image'])
        embed.add_field(name='Price',value=guitar['price'],inline=True)
        embed.add_field(name='Rating',value=guitar['rating'],inline=True)
        embed.add_field(name='Brand',value=guitar['brand'],inline=True)
        return embed

    async def get_andertons_data(self, url):
        page = await self.make_soup(url)
        guitar = {}
        guitar['url'] = url
        guitar['title'] = page.find('span',{'itemprop':'name'}).contents[0]
        guitar['image'] = page.find('meta',{'property':'og:image'}).get('content')
        try:
            guitar['rating'] = len(page.find('span',{'class':'feefo-stars feefo-stars--yellow'}).find_all('i',{'class':'icon-amc-star'}))
            guitar['rating'] = ''.join(['⭐' for i in range(0,guitar['rating'])])
        except AttributeError:
            guitar['rating'] = 'N/A'
        guitar['price'] = page.find('span',{'class':'product-price'}).contents[0].strip()
        specs = page.find('table',{'class':'pdp-descriptive-attributes'})
        def get_spec(name):
            return [i.find('td',{'class':'pdp-descriptive-attributes__value'}).contents[0].strip() for i in specs.find_all('tr',{'class':'pdp-descriptive-attributes__item'}) if i.find('td',{'class':'pdp-descriptive-attributes__name'}).contents[0].strip() == name][0]
        guitar['brand'] = get_spec('Brand:')
        return guitar

    async def get_pmt_data(self, url):
        page = await self.make_soup(url)
        guitar = {}
        guitar['url'] = url
        guitar['title'] = page.find('span',{'itemprop':'name'}).contents[0]
        guitar['image'] = page.find('meta',{'property':'og:image'}).get('content')
        guitar['price'] = page.find('span',{'class':'price'}).contents[0].strip()
        specs = page.find('table',{'class':'data table additional-attributes'})
        def get_spec(name):
            return specs.find('td',{'data-th':name}).contents[0]
        guitar['brand'] = get_spec('Manufacturer')
        guitar['rating'] = 'N/A'
        return guitar

    async def get_thomann_data(self, url):
        page = await self.make_soup(url)
        guitar = {}
        guitar['url'] = url
        guitar['title'] = page.find('meta',{'property':'og:title'}).get('content')
        guitar['image'] = page.find('meta',{'property':'og:image'}).get('content')
        guitar['price'] = page.find('div',{'class':'prod-pricebox-price'}).find('span',{'class':'primary'}).contents[0]
        guitar['brand'] = page.find('div',{'class':'rs-prod-manufacturer-logo'}).find('img').get('alt')
        rating = page.find('span',{'class':'rs-stars'}).find('span',{'class':'overlay-wrapper'}).get('style').split('width: ')[1].split('%')[0]
        guitar['rating'] = ''.join(['⭐' for i in range(0,round(5 * (float(rating) / 100)))])
        return guitar

    async def make_soup(self, url):
        async with aiohttp.ClientSession() as session:
            data = await session.get(url,headers=headers)
            text = await data.text()
            await session.close()
        page = Soup(text,'html.parser')
        return page

def setup(client):
    client.add_cog(Guitar(client))
