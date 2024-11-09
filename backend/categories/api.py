from backend.google_cloud.api import GoogleCloudAPI


class CategoriesAPI():

    def __init__(self):
        self.__client = GoogleCloudAPI()
        self.__pull_data()


    def get_expenditure_categories(self):
        return self.__expenditure_categories 
    

    def __pull_data(self):
        sql = f"""
        SELECT
            Name,
            Type
        FROM 
            {self.__client._dataset}.d_category
        GROUP BY
            1, 2 -- Group for case of duplication
        """
        df = self.__client.sql_to_pandas(sql)
        self.__df = df
        self.__refresh()


    def __refresh(self):
        self.__expenditure_categories = self.__df.loc[self.__df['Type'] == 'expenditure', 'Name'].to_list()
        self.__asset_categories = self.__df.loc[self.__df['Type'] == 'asset', 'Name'].to_list()