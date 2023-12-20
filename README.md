# aplus_mobile_fcm_server

A+つくばネイティブアプリのためのFCMサーバ（通知バックエンド）

## 起動方法
A+つくばの本体のdockerを起動し後に，`docker compose up -d`で起動します．

## 環境構築
`firebaseServiceAccountKey.json`を入手して，ルートにおいてください．

初回実行時は，`docker exec -it a_plus_tsukuba-fcm bash`で中に入り，`python manage.py migrate`等が必要です．

## APIs
### アプリ起動時などに確認するもの

1. `api/device`でデバイスが無効になってないか確認（場合によっては通知権限をリクエストする）
    - `api/device/activate`で有効化をリクエストできる
2. `api/device/subscription`で購読情報を確認する

### 購読スレッドを追加する

`api/<thread_id>/subscribe`で登録する．デバイスレコードや購読情報レコードが未作成の場合は新規作成される．

A+つくばに存在しないスレッドIDも登録できるので注意