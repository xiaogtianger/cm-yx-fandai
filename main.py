import json
import csv
import time
import urllib.request


API_URL = "https://zip.cm.edu.kg/all.json"


# =========================================================
# 通用 API 获取
# =========================================================

def fetch_api():

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }


    for retry in range(3):

        try:

            print(f"正在请求 API 第 {retry+1} 次")

            req = urllib.request.Request(
                API_URL,
                headers=headers
            )

            with urllib.request.urlopen(
                req,
                timeout=30
            ) as response:

                data = response.read().decode("utf-8")

                return json.loads(data)


        except Exception as e:

            print(
                f"API失败: {e}"
            )

            time.sleep(5)


    print("API连续失败，终止")

    return None



def parse_nodes(raw):

    if isinstance(raw,list):

        return raw


    if isinstance(raw,dict):

        result=[]

        for v in raw.values():

            if isinstance(v,list):

                result.extend(v)


        return result


    return []



# =========================================================
# 精品 VLESS TXT
# =========================================================

def generate_vless(nodes):


    TARGET_ASNS = {
        906,
        25820,
        32097,
        63888,
        396982,
        137929,
        40065,
        135064,
        4809,
        9929,
        58453,
        36002,
        8143
    }


    NICKNAMES={

        "36002":"狗妈",
        "8143":"奶爸",
        "906":"大妈",
        "396982":"Google LLC",
        "137929":"亚太大妈",
        "58453":"移动 CMI",
        "25820":"搬瓦工",
        "9929":"联通A网",
        "63888":"Datawing Limited",
        "135064":"Rio Tinto IS&T",
        "4809":"电信CN2",
        "40065":"CNSERVERS",
        "32097":"WholeSale Internet"

    }



    result=[]

    seen=set()

    index=0



    for item in nodes:


        if not isinstance(item,dict):

            continue



        meta=item.get("meta",{})



        port = (
            item.get("_port")
            or meta.get("_port")
            or (
                item.get("port")[0]
                if isinstance(item.get("port"),list)
                and item.get("port")
                else None
            )
        )


        if not port:

            continue



        asn=meta.get("asn")

        try:

            asn_int=int(asn)

        except:

            continue



        if asn_int not in TARGET_ASNS:

            continue



        country=meta.get(
            "country",
            "Unknown"
        )



        org_name=NICKNAMES.get(
            str(asn_int),
            f"AS{asn_int}"
        )



        ips=[

            item.get("ip"),

            meta.get("clientIp")

        ]



        for ip in ips:


            if not ip:

                continue


            if ip in seen:

                continue


            seen.add(ip)



            show_ip = (
                f"[{ip}]"
                if ":" in ip
                else ip
            )


            index+=1


            name=(
                f"CM_{org_name}_{country}_{index:02d}"
            )


            result.append(
                f"{show_ip}:{port}#{name}"
            )



    if result:


        with open(
            "vless_api_all.txt",
            "w",
            encoding="utf-8"
        ) as f:


            f.write(
                "\n".join(result)
            )



    print(
        f"VLESS生成完成: {len(result)} 条"
    )





# =========================================================
# CSV生成
# =========================================================

def generate_csv(nodes):


    ipv4=[]

    ipv6=[]


    v4_seen=set()

    v6_seen=set()



    for item in nodes:


        if not isinstance(item,dict):

            continue



        meta=item.get(
            "meta",
            {}
        )



        port=(

            item.get("_port")

            or meta.get("_port")

            or (
                item.get("port")[0]
                if isinstance(item.get("port"),list)
                and item.get("port")
                else None
            )

        )


        if not port:

            continue



        ips=[

            item.get("ip"),

            meta.get("clientIp")

        ]



        for ip in ips:


            if not ip:

                continue



            if ":" in str(ip):

                key=f"{ip}:{port}"

                if key not in v6_seen:

                    v6_seen.add(key)

                    ipv6.append(
                        {
                            "ip":ip,
                            "port":port
                        }
                    )


            else:


                key=f"{ip}:{port}"


                if key not in v4_seen:

                    v4_seen.add(key)

                    ipv4.append(
                        {
                            "ip":ip,
                            "port":port
                        }
                    )




    headers=[
        "ip",
        "port"
    ]



    if ipv4:

        with open(
            "cm中转ipv4.csv",
            "w",
            encoding="utf-8",
            newline=""
        ) as f:


            w=csv.DictWriter(
                f,
                fieldnames=headers,
                lineterminator="\n"
            )

            w.writeheader()

            w.writerows(ipv4)



    if ipv6:

        with open(
            "cm中转ipv6.csv",
            "w",
            encoding="utf-8",
            newline=""
        ) as f:


            w=csv.DictWriter(
                f,
                fieldnames=headers,
                lineterminator="\n"
            )

            w.writeheader()

            w.writerows(ipv6)



    print(
        f"CSV完成 IPv4:{len(ipv4)} IPv6:{len(ipv6)}"
    )





# =========================================================
# 主程序
# =========================================================


if __name__=="__main__":


    raw=fetch_api()


    if not raw:

        exit(1)



    nodes=parse_nodes(raw)



    print(
        f"解析节点数量:{len(nodes)}"
    )



    generate_vless(nodes)


    generate_csv(nodes)


    print(
        "全部任务完成"
    )
