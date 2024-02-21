import os
import sqlite3
from .curse import words


class Sea:
    def __init__(self, event):
        self.usr = event.user_id
        self.grp = getattr(event, "group_id", None)
        self.name = event.sender.card
        self.db = sqlite3.connect(os.path.dirname(
            __file__) + "/bottle.db", check_same_thread=False)
        self.cursor = self.db.cursor()

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS bottles (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, user TEXT, _group TEXT, msg TEXT, time TEXT);")
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS ban (id INTEGER PRIMARY KEY AUTOINCREMENT, uin TEXT, type TEXT, time TEXT);")
        self.db.commit()


    def contains_prohibited_words(self, text):
        for word in words:
            if word in text:
                return True
        return False

    def throw(self, msg):
        if not self.is_ban():
            if not msg or msg == "" or len(msg) < 10:
                return "需要投递的内容过少"
            elif len(msg) > 1000:
                return "需要投递的内容过长"
            elif self.contains_prohibited_words(msg):
                return "发现违禁词，请更换投递内容"
            else:
                try:
                    self.db.execute(
                        "INSERT INTO bottles (name, user, _group, msg, time) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP);", (self.name, self.usr, self.grp, msg))
                    self.db.commit()
                except Exception as e:
                    return "发生错误：{}".format(str(e))
                finally:
                    return "已经帮你丢出去了哦~"

    def pick(self, id=None):
        if not self.is_ban():
            try:
                if not id or not str(id).isdigit():
                    sql = "SELECT * FROM bottles ORDER BY RANDOM() LIMIT 1;"
                    self.cursor.execute(sql)
                else:
                    sql = "SELECT * FROM bottles WHERE id = ? LIMIT 1;"
                    self.cursor.execute(sql, (id,))
                self.db.commit()
                row = self.cursor.fetchone()
                return row if row else None
            except Exception as e:
                return str(e)

    def remove(self, id):
        try:
            self.cursor.execute("DELETE FROM bottles WHERE id = ?;", (id,))
            self.db.commit()
        except Exception as e:
            return "发生错误：{}".format(str(e))
        finally:
            return "成功删除id为 {} 的漂流瓶".format(id)

    def clear(self):
        try:
            self.cursor.execute("DELETE FROM bottles;")
            self.db.commit()
            count = self.cursor.rowcount
        except Exception as e:
            return "发生错误：{}".format(str(e))
        finally:
            count = count if "count" in locals() else 0
            return "已删除 {} 个漂流瓶".format(count)
        
    def ban(self, msg):
        _type, uin = msg.split()
        if _type == "group":
            if not self.is_ban(uin):
                try:
                    self.db.execute(
                        "INSERT INTO ban (uin, type, time) VALUES (?, ?, CURRENT_TIMESTAMP);", (uin, _type))
                    self.db.commit()
                    return "已将群聊:{} 拉入黑名单".format(uin)
                except Exception as e:
                    return "发生错误：{}".format(str(e))
            else:
                return "该群已在黑名单内"
        elif _type == "user":
            if not self.is_ban(uin):
                try:
                    self.db.execute(
                        "INSERT INTO ban (uin, type, time) VALUES (?, ?, CURRENT_TIMESTAMP);", (uin, _type))
                    self.db.commit()
                    return "已将用户({})拉入黑名单".format(uin)
                except Exception as e:
                    return "发生错误：{}".format(str(e))
            else:
                return "该用户已在黑名单内"
        else:
            return "未知操作"
    
    def clear_ban(self):
        try:
            self.cursor.execute("DELETE FROM ban;")
            self.db.commit()
            count = self.cursor.rowcount
        except Exception as e:
            return "发生错误：{}".format(str(e))
        finally:
            count = count if "count" in locals() else 0
            return "已移除 {} 个黑名单记录".format(count)
        
    def ban_list(self):
        try:
            self.cursor.execute("SELECT uin, type, time FROM ban;")
            rows = self.cursor.fetchall()
            if not rows:
                return "当前没有任何黑名单记录"
            else:
                bans = ["|uin|type|time|"]
                for row in rows:
                    ban_str = "{}({})[{}]".format(row[0], row[1], row[2])
                    bans.append(ban_str)
                return "当前黑名单列表：{}".format(",\n".join(bans))
        except Exception as e:
            return "发生错误：{}".format(str(e))
    
    def remove_ban(self, msg):
        _type, uin = msg.split()
        if _type == "group":
            if self.is_ban(uin):
                try:
                    self.cursor.execute(
                        "DELETE FROM ban WHERE uin = ? and type = ?;", (uin, _type))
                    self.db.commit()
                    return "已将群聊:{} 移出黑名单".format(uin)
                except Exception as e:
                    return "发生错误：{}".format(str(e))
            else:
                return "该群不在黑名单内"
        elif _type == "user":
            if self.is_ban(uin):
                try:
                    self.cursor.execute(
                        "DELETE FROM ban WHERE uin = ? and type = ?;", (uin, _type))
                    self.db.commit()
                    return "已将用户({})移出黑名单".format(uin)
                except Exception as e:
                    return "发生错误：{}".format(str(e))
            else:
                return "该用户不在黑名单内"
        else:
            return "未知操作"

    def is_ban(self):
        if self.grp:
            uin = self.grp
            _type = "group"
        else:
            uin = self.usr
            _type = "user"
        self.cursor.execute(
            "SELECT COUNT(*) FROM ban WHERE uin=? and type=?;", (uin, _type))
        result = self.cursor.fetchone()
        if result[0] > 0:
            return True
        return False
