from ..ImageRepositoryInterface import ImageRepository, ImageEntity
from ..repositories import *
from datetime import datetime
from ...database import Database, CursorFromConnectionPool
from pathlib import Path
from psycopg2 import DatabaseError
import os, logging, io, traceback
from ...feature_extractor import FeatureExtractor
from PIL import Image
import numpy as np
from ...models.image import URL_SERVER


logger = logging.getLogger()

fe = FeatureExtractor()


class NewImageRepository(ImageRepository):
    def upload_image(self, image_entity: ImageEntity, image_name: str) -> RepoResponse:
        image_entity.generate_id()
        image_entity.hash_name_generator(image_name)
        image_entity.make_symlink()
        now = datetime.now()

        driver_path = Path(os.path.dirname(__file__)).parent.__str__() + "/driver/" + os.getenv("DRIVER")
        insert_script = driver_path + "/create.sql"
        query_stmt = open(insert_script, 'r').read()

        value =  [
            str(image_entity.id),
            now.timestamp().__int__(),
            image_entity.texture,
            image_entity.hash_name,
        ]

        status = []
        result = []
        except_type, except_value, except_traceback = None, None, None
        try:
            db_connc = CursorFromConnectionPool()
            ps_cursor = db_connc.__enter__()
            ps_cursor.execute(query_stmt,value)

            # Enable logging when inserting to database
            for element in range(0,len(value) -1):
                # Shorten binary data cause it's too large
                if isinstance(value[element], bytes):
                    value[element] = "[binary data]"
            logger.info("INSERTED VALUES: " + str(value))

            status = Uploaded
            result = image_entity
        except (Exception, DatabaseError) as error:
            logger.error(error)

            except_type = type(error).__name__
            except_value = error.args
            except_traceback = traceback.format_exc()
       
        finally:
            db_connc.__exit__(except_type, except_value, except_traceback)

        return status, result

    def load_more_images(self, offset: int, limit: int) -> RepoResponse:
        driver_path = Path(os.path.dirname(__file__)).parent.__str__() + "/driver/" + os.getenv("DRIVER")
        load_more_script = driver_path + "/load_more.sql"
        query_stmt = open(load_more_script, 'r').read()

        result = []
        except_type, except_value, except_traceback = None, None, None
        value = [
            limit,
            offset
        ]

        try:
            db_connc = CursorFromConnectionPool()
            ps_cursor = db_connc.__enter__()

            ps_cursor.execute(query_stmt, value)
            # Format result as list of dicts
            album = []
            for buff in ps_cursor:
                row = {}
                c = 0
                for col in ps_cursor.description:
                    row.update({str(col[0]): buff[c]})
                    c += 1

                album.append(row.copy())

        except (Exception, DatabaseError) as error:
            logger.error(error)

            except_type = type(error).__name__
            except_value = error.args
            except_traceback = traceback.format_exc()
       
        finally:
            db_connc.__exit__(except_type, except_value, except_traceback)

        status = Success
        result = album
        return status, result

    def search_image(self, texture: bytes, album: Any) -> RepoResponse:

        status = []
        result = []
        
        if len(album) == 0:
            status = NotFound
            return status, result

        status = Success
        result = find_similiar_images(album, texture)
        return status, result

    def get_image_by_name(self, name: str) -> RepoResponse:
        driver_path = Path(os.path.dirname(__file__)).parent.__str__() + "/driver/" + os.getenv("DRIVER")
        select_script = driver_path + "/get_by_name.sql"
        query_stmt = open(select_script, 'r').read()

        status = []
        result = {}
        except_type, except_value, except_traceback = None, None, None
        value = [
            name,
        ]
        try:
            db_connc = CursorFromConnectionPool()
            ps_cursor = db_connc.__enter__()

            ps_cursor.execute(query_stmt, value)
            # Format result as dict
            for buff in ps_cursor:
                row = {}
                c = 0
                for col in ps_cursor.description:
                    row.update({str(col[0]): buff[c]})
                    c += 1

                result = row.copy()

        except (Exception, DatabaseError) as error:
            logger.error(error)

            except_type = type(error).__name__
            except_value = error.args
            except_traceback = traceback.format_exc()
       
        finally:
            db_connc.__exit__(except_type, except_value, except_traceback)
        
        if len(result) == 0:
            status = GetError
            return status, result

        status = Success
        return status, result

def find_similiar_images(album: list, input: Image):
    features = get_np_arrays_from_album(album) 
    
    # Run Search Algorithm
    query = fe.extract(input)
    dists = np.linalg.norm(features-query, axis=1)  # L2 distances to features
    ids = np.argsort(dists)[:2]  # Top 30 results
    scores = [(dists[id], album[id]) for id in ids]

    resault = []

    for item in scores:
        # Make coppy the dict so not effect old dict's values after use del method
        photo = dict(item[1])

        """
        For getting more nearly similar images, 
        the threshold should be enabled,preventing different images as much as possible
        Example: A similar image's distances can between 0 and 1
        Note: Threshold can be changed for many suitable cases
            The lower Distance, the more similar images
            A variety of An Image can be in suitable Thresholds chose
            Ex: If Threshold between 0 and 0.5 it variety may not be shown caused the narrow of threshold  
        """
        if item[0] > 1.1:
            continue

        data = {
            "persent": str(item[0]),
            "link": URL_SERVER + str(photo['hash_name'])
        }
        del photo['texture']
        del photo['hash_name']
        data.update(photo)

        resault.append(data)

    return resault


def get_np_arrays_from_album(album: list):
    output = []
    for photo in album:
        texture_bytes = io.BytesIO(photo['texture'])
        img = Image.open(texture_bytes)
        np_array = fe.extract(img)
        output.append(np_array)

    return output

