## 1. Landsat公开数据基本介绍

Landsat公开数据集包含collection1和collection2。

[Landsat Collection 2 Level-2 Science Products | U.S. Geological Survey (usgs.gov)](https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products)

- Collection 1 包含1972年至今所有 Landsat 1-8的 Level 1 数据。

- Collection 2 包括自 1972 年以来所有传感器的Level 1 数据，以及从 1982 年至今的**全球 Level 2 地表反射率**和地表温度产品。Level-2 科学产品是根据 Collection 2 Level-1 经过辐射校正、大气校正生成的，并满足 <76 度太阳天顶角约束。

Collection 2 的出现是因为Landsat Level 1 数据的又一次重大再处理，显著提高了绝对地理定位精度。

因此，我们选择Collection 2 Level-2产品进行下载。

## 2. Landsat数据命名及tile分布

### 2.1 命名方式

[What is the naming convention for Landsat Collections Level-1 scenes? | U.S. Geological Survey (usgs.gov)](https://www.usgs.gov/faqs/what-naming-convention-landsat-collections-level-1-scenes)

LXSS_LLLL_PPPRRR_YYYYMMDD_yyyymmdd_CC_TX

- L = Landsat
- X = Sensor (“C”=OLI/TIRS combined, “O”=OLI-only, “T”=TIRS-only, “E”=ETM+, “T”=“TM, “M”=MSS)
- SS = Satellite (”07”=Landsat 7, “08”=Landsat 8)
- LLL = Processing correction level (L1TP/L1GT/L1GS)
- **PPP = WRS path. Ascending or descending path of the satellite**
- **RRR = WRS row. The north-south row that sectionalizes WRS**
- YYYYMMDD = Acquisition year, month, day
- yyyymmdd - Processing year, month, day
- CC = Collection number (01, 02, …)
- TX = Collection category (“RT”=Real-Time, “T1”=Tier 1, “T2”=Tier 2)

**Example:** LC08_L1GT_029030_20151209_20160131_01_RT

**Means**: Landsat 8; OLI/TIRS combined; processing correction level L1GT; path 029; row 030; acquired December 9, 2015; processed January 31, 2016; Collection 1; Real-Time

### 2.2 tile分布

[Landsat Shapefiles and KML Files | U.S. Geological Survey (usgs.gov)](https://www.usgs.gov/landsat-missions/landsat-shapefiles-and-kml-files)

WRS tile编码为6位数字PPPRRR。WRS 是对 Landsat 数据的全球编码。 Landsat 卫星 1、2 和 3 使用WRS-1，Landsat 卫星 4、5、7 和 8 使用 WRS-2。

- **PPP = WRS path. Ascending or descending path of the satellite**

- **RRR = WRS row. The north-south row that sectionalizes WRS**

    

    中国海岸线相交tile为56个（包括台湾省）。

    ```
    ['124_46', '123_46', '125_45', '124_45', '123_45', '122_45', '121_45', '122_44', '121_44', '120_44', '119_44', '120_43', '119_43', '118_43', '119_42', '118_42', '118_41', '117_41', '118_40', '117_40', '118_39', '117_39', '119_38', '118_38', '119_37', '118_37', '121_36', '120_36', '119_36', '120_35', '119_35', '118_35', '122_34', '121_34', '120_34', '119_34', '118_34', '122_33', '121_33', '120_33', '119_33', '118_33', '121_32', '120_32', '119_32', '118_32', '120_31', '125_47', '124_47', '123_47', '125_46', '117_45', '118_44', '117_44', '117_43', '117_42']
    ```

    江苏省海岸线相交tile为7个。

    ```
    ['119_38', '118_38', '119_37', '118_37', '121_36', '120_36', '119_36']
    ```

    > 注意以上作为tile id在检索时应将“_”替换为0



## 3. 不同数据源数据对比

以江苏省海岸线某景数据为例。

`LC09_L2SP_120036_20231018_20231019_02_T1`

4个数据源（后两个aws的需要付费）：

- [Data Access | Landsat Science (nasa.gov)](https://landsat.gsfc.nasa.gov/data/data-access/)
- [Landsat Collection 2 Level-2 | Planetary Computer --- Landsat Collection 2 2 级 |行星计算机 (microsoft.com)](https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2)

- https://earth-search.aws.element84.com/v1/
- [USGS Landsat - Registry of Open Data on AWS](https://registry.opendata.aws/usgs-landsat/)

经对比，不同来源的数据值一致，值范围一致，空值一致，行列数一致， stac的元数据一致。

![image-20231209174604971](./Landsat%E6%95%B0%E6%8D%AE%E4%B8%8B%E8%BD%BD.assets/image-20231209174604971.png)



![image-20231209174755109](./Landsat%E6%95%B0%E6%8D%AE%E4%B8%8B%E8%BD%BD.assets/image-20231209174755109.png)

## 4. 从微软pc下载数据

**卫星选择**

landsat-7卫星传感器坏了，landsat5服役到2013年，landsat8、9最新最好，因此选择5、8、9三个卫星的数据。

**时间范围**

从2000-至今。

先下载一年的



**assets选择**

暂时不确定

[Landsat Collection 2 Level-2 | Planetary Computer (microsoft.com)](https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2)

![9fc262d3a42db8b60ffc53acfb9f45d](./Landsat%E6%95%B0%E6%8D%AE%E4%B8%8B%E8%BD%BD.assets/9fc262d3a42db8b60ffc53acfb9f45d.png)



## 5. 下载程序的使用

```bash
# 配置环境
conda create -n downloadls python=3.9
conda activate downloadls
pip install pystac_client planetary_computer

# 程序调用
python landsat_download.py --start_date 2023-01-01 --end_date 2023-02-01 --wrs 120036 --output /mnt/disk/huangkw/landsat-jiangsu-coastline/ --cloud_cover 20


```





