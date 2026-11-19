# nether-craft

## ピグリン交易拡張

Minecraft統合版1.21.90以降向けのビヘイビアーパックです。既存の交易候補を残し、以下の7品目を追加します。

| 追加品目 | 個数 | 抽選重み | 確率 |
|---|---|---|---|
| 土 | 8〜16 | 40 | 約7.17% |
| ビートルートの種 | 2〜4 | 20 | 約3.58% |
| ダイヤモンド | 1 | 2 | 約0.36% |
| ラピスラズリ | 4〜8 | 10 | 約1.79% |
| 銅ブロック | 1 | 10 | 約1.79% |
| 鶏のスポーンエッグ | 1 | 2 | 約0.36% |
| サドル | 1 | 5 | 約0.90% |

追加後の重み合計は558です。砂利は土と同じ約7.17%です。既存候補の個数と重みは維持していますが、品目追加により既存候補の出現確率は下がります。

## 導入・調整

配布用の`.mcaddon`は`dist/`に配置します。生成物のため、`.gitignore`でGit管理から除外しています。

`manifest.json`を含むこのフォルダをビヘイビアーパックとして導入します。スクリプト・追加ライブラリ・リソースパックは不要です。

詳しい導入手順と調整方法は[導入ガイド](../../doc/materials/guide/nether_craft_setup.md)を参照してください。

サーバー1.26.66.1でパック読み込みを確認済みです。ゲーム内の交易は未検証です。同じ`loot_tables/entities/piglin_barter.json`を変更する別パックと競合します。

## ビルドとGitHub Releases

このリポジトリのルートで、Python標準ライブラリだけでビルドできます。

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_addon.py
```

出力先は`dist/nether-craft-<version>.mcaddon`です。README・Git情報・スクリプト・テストは配布物に含めません。

GitHub Actionsはプルリクエストとmainへのpushでテスト・ビルドを実行します。`v1.0.0`のようなタグのpushでは、成功後にGitHub Releaseを作成して`.mcaddon`を添付します。手動でのファイル添付や追加のアクセストークン登録は不要です。

1. `manifest.json`の`header.version`と`modules[].version`をリリースする版番号に揃えます。
2. ソース・ワークフロー・テストをコミットしてpushします。`dist/`はコミットしません。
3. そのコミットに`v<version>`タグを付けてpushします。タグとmanifestの版番号が違う場合は公開前に失敗します。
4. リポジトリのActionsで成功を確認し、Releasesから`.mcaddon`をダウンロードします。

このプロジェクトではGitの変更操作を指定のmomo-gitコンテナ内で行います。以下は1.0.0を公開する場合の操作例です（自動では実行しません）。

```sh
git tag v1.0.0
git push origin v1.0.0
```

リリース済みのタグは再利用せず、次の版番号で公開してください。ワールドのパック登録も版番号に合わせて更新します。Actionsの書き込みを組織設定で禁止している場合は、リリース作成に必要な`contents: write`を許可する必要があります。

設定の根拠：[checkout公式](https://github.com/actions/checkout)、[GitHub CLIのrelease create](https://cli.github.com/manual/gh_release_create)。
