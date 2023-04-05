import aiofiles.os


async def get_file_size(file):
    stat = await aiofiles.os.stat(file)
    return stat.st_size
