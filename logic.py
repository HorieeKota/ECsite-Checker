from playwright.sync_api import sync_playwright
import time
import random

def check_site(url, check_type):
    """
    URLを見て、Amazonか楽天か判断し、適切な関数を呼び出す「司令塔」
    """
    if "amazon" in url:
        return check_amazon(url, check_type)
    elif "rakuten" in url:
        return check_rakuten(url, check_type)
    else:
        return {"status": "error", "value": None, "message": "対応していないサイトです"}

def check_rakuten(url, check_type):
    """
    楽天用のチェック関数
    """
    result = {"status": "error", "value": None, "message": ""}
    
    try:
        with sync_playwright() as p:
            # 楽天はBot対策がAmazonほど厳しくないので標準設定でOK
            # headless=False にして画面を表示
            browser = p.chromium.launch(headless=False) 
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            print(f"楽天へアクセス中: {url} ...")
            page.goto(url, timeout=60000)
            time.sleep(3) # 読み込み待ち

            if check_type == "PRICE":
                # --- 楽天の価格チェック ---
                # 楽天の商品ページは大抵 ".price2" というクラスに価格がある
                # 見つからない場合はメタデータなどを探す
                price_selectors = [".price2", "#priceCalculationConfig .price", "span[itemprop='price']"]
                
                price_text = None
                for selector in price_selectors:
                    if page.query_selector(selector):
                        price_text = page.query_selector(selector).inner_text().strip()
                        break
                
                if price_text:
                    # "4,980円" -> 4980 に変換
                    price_val = int(price_text.replace(",", "").replace("円", ""))
                    result["status"] = "success"
                    result["value"] = price_val
                else:
                    result["message"] = "価格が見つかりませんでした"

            elif check_type == "STOCK":
                # --- 楽天の在庫チェック ---
                # 「商品をかごに追加」などのボタンがあるか探す
                
                # 1. 「かご」関係のボタンがあるか？
                # 文字で探す（"かごに追加", "商品をかごに追加" など）
                has_cart_button = False
                if page.get_by_text("かごに追加").count() > 0:
                    has_cart_button = True
                elif page.get_by_text("商品をかごに追加").count() > 0:
                    has_cart_button = True
                elif page.query_selector(".cart-button, .new_cart_button, #add-cart-button"):
                    has_cart_button = True
                
                # 2. 「売り切れ」の文字があるか？
                is_sold_out = False
                if page.get_by_text("売り切れ").count() > 0:
                    is_sold_out = True
                
                # 判定
                if has_cart_button:
                    result["status"] = "success"
                    result["value"] = "かごに追加 (在庫あり)"
                elif is_sold_out:
                    result["status"] = "success"
                    result["value"] = "売り切れ"
                else:
                    # どちらも見つからない場合も、エラーにせず状況を返す
                    result["status"] = "success"
                    result["value"] = "在庫状況不明(ボタンなし)"

            context.close()
            browser.close()

    except Exception as e:
        print(f"★楽天エラー: {e}")
        result["message"] = f"エラー: {str(e)}"

    return result

def check_amazon(url, check_type):
    """
    Amazon用のチェック関数
    """
    result = {"status": "error", "value": None, "message": ""}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=500)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            print(f"Amazonアクセス中: {url} ...")
            page.goto(url, timeout=60000)
            time.sleep(random.uniform(2, 5))

            if check_type == "PRICE":
                selectors = [".a-price-whole", "#corePriceDisplay_desktop_feature_div .a-price-whole", ".apexPriceToPay .a-offscreen"]
                price_text = None
                for selector in selectors:
                    element = page.query_selector(selector)
                    if element:
                        price_text = element.inner_text().strip()
                        break
                
                if price_text:
                    price_val = int(price_text.replace(",", "").replace("￥", "").split("\n")[0])
                    result["status"] = "success"
                    result["value"] = price_val
                else:
                    result["message"] = "価格が見つかりませんでした"

            elif check_type == "STOCK":
                selectors = ["#availability", "#outOfStock"]
                stock_text = None
                for selector in selectors:
                    element = page.query_selector(selector)
                    if element:
                        stock_text = element.inner_text().strip()
                        break

                if stock_text:
                    result["status"] = "success"
                    result["value"] = stock_text
                elif page.query_selector("#add-to-cart-button"):
                    result["status"] = "success"
                    result["value"] = "カートに入れる (在庫あり)"
                else:
                    result["message"] = "在庫情報が見つかりませんでした"

            context.close()
            browser.close()

    except Exception as e:
        print(f"★Amazonエラー: {e}")
        result["message"] = f"エラー: {str(e)}"

    return result