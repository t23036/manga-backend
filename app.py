from fastapi import FastAPI #FastAPIの本体をインポート
from fastapi.middleware.cors import CORSMiddleware #CORSミドルウェアをインポート
from pydantic import BaseModel #リクエストデータのバリエーション用
from fastapi.responses import JSONResponse #JSON形式でレスポンスを返すために使用
from typing import Optional #任意の(Noneを許容する)フィールドを定義するために使用
import sqlite3 #SQLiteデータベースに接続するための標準モジュール

class Item(BaseModel): #POSTで受け取るデータの構造テーブルを定義
    query1: Optional[str] = None #タイトル又は作者名を受け取る

app = FastAPI() #FastAPIアプリケーションの初期化

app.add_middleware( #CORSの設定(異なるオリジン(場所)からのアクセスを許可)これがないとセキュリティが危ないし、検索できない
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, #認識情報を含めるかどうか(今回は含めない)
    allow_methods=["*"], #全てのHTTPメソッドの許可　なんで＊なのか説明できるようにしておく
    allow_headers=["*"], #全てのHTTPヘッダーの許可
)

@app.post("/search") #POSTリクエストで/searchにアクセスされたときの処理
def search_users(item: Item): #リクエストボディをItemクラスとして受け取る
    with sqlite3.connect('./example2.db') as conn: #SQLiteデータベースの接続(自動で閉じる)
        cursor = conn.cursor() #SQLを実行するためのカーソルを取得

        if item.query1: #query1に値がある場合(検索条件あり)
            cursor.execute( #manga(タイトル)またはname(作者名)で検索（完全一致）
                "SELECT * FROM users WHERE manga = ? OR name = ?" "OR artist = ?", 
                (item.query1, item.query1, item.query1) #プレースホルダー("?")でSQLインジェクション対策
            )
        else: #query1がNoneの場合(検索条件なし)
            cursor.execute("SELECT * FROM users") #全レコードを取得

        rows = cursor.fetchall() #結果を全て取得(リストで返る)

        results = [ #データベースの各行を辞書形式に変換
            {
                "example_id": row[0], #ID
                "manga": row[1], #漫画のタイトル
                "name": row[2], #作者名
                "artist": row[3], #作画者名
                "release": row[4], #発売日
                "fupdate": row[5], #最終更新日
                "popular": row[6], #人気度
                "image": row[7] #画像
            }
            for row in rows #rowsの各行についてループ
        ]

        return JSONResponse(content=results) #JSONレスポンスとして返す
