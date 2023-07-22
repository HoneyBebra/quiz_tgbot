import sqlite3


class WWWStatistics:
    def __init__(self):
        self.connection = sqlite3.connect("local_data/WWW_stat.db")
        self.cursor = self.connection.cursor()

    def create_table_fi_not_exists(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Statistics (
                user_id VARCHAR(255), 
                stat_right BIGINT UNSIGNED, 
                stat_wrong BIGINT UNSIGNED
            )
            """
        )

    def user_statistics_update(self, user_id, right_answer):
        answer_result = {
            True: (1, 0),
            False: (0, 1)
        }
        # check if the user is in the database
        user_existence = len(self.cursor.execute(
            f"""
                    SELECT * FROM Statistics 
                    WHERE user_id = {user_id}
                    """
        ).fetchall())
        if user_existence == 0:
            self.cursor.execute(
                f"""
                INSERT INTO Statistics (user_id, stat_right, stat_wrong) 
                VALUES ({user_id}, 
                    {answer_result[right_answer][0]}, 
                    {answer_result[right_answer][1]})
                """
                )
        else:
            self.cursor.execute(
                f"""
                UPDATE Statistics 
                SET stat_right = stat_right + {answer_result[right_answer][0]},
                stat_wrong = stat_wrong + {answer_result[right_answer][1]}
                WHERE user_id = {user_id}
                """
                )
        self.connection.commit()

    def get_user_statistics(self, user_id):
        return self.cursor.execute(
            f"""
            SELECT stat_right, stat_wrong FROM Statistics WHERE user_id = {user_id}
            """
            ).fetchall()

