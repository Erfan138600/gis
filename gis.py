# -*- coding: utf-8 -*-
"""
GIS آموزشی حرفه‌ای فارسی - نسخه کامل
ساخته شده با Python + CustomTkinter + Geopandas + Folium
نویسنده: دستیار هوش مصنوعی شما :)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import geopandas as gpd
import folium
from folium.plugins import Draw, MeasureControl
import os
import webbrowser
from tkinter import font
import pandas as pd

# تنظیمات ظاهری
ctk.set_appearance_mode("dark")  # dark یا light
ctk.set_default_color_theme("blue")

class EducationalGIS(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("🌍 سیستم اطلاعات جغرافیایی آموزشی - نسخه حرفه‌ای")
        self.geometry("1400x900")
        self.minsize(1200, 700)
        
        # فونت فارسی
        try:
            persian_font = font.Font(family="Tahoma", size=11)
            persian_font_bold = font.Font(family="Tahoma", size=12, weight="bold")
        except:
            persian_font = None
            persian_font_bold = None

        # متغیرهای داده
        self.input_gdf = None
        self.processed_gdf = None
        self.output_path = None

        # ساخت تب‌ها
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        self.tabview.add("ورودی داده‌ها")
        self.tabview.add("پردازش جغرافیایی")
        self.tabview.add("خروجی و نمایش")

        # تب ورودی
        self.create_input_tab()

        # تب پردازش
        self.create_processing_tab()

        # تب خروجی
        self.create_output_tab()

    def create_input_tab(self):
        tab = self.tabview.tab("ورودی داده‌ها")

        # فریم سمت چپ - انتخاب فایل
        left_frame = ctk.CTkFrame(tab)
        left_frame.pack(side="left", fill="y", padx=20, pady=20)

        ctk.CTkLabel(left_frame, text="📥 بارگذاری داده‌های جغرافیایی", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)

        ctk.CTkButton(left_frame, text="انتخاب Shapefile (.shp)", 
                     command=self.load_shapefile, height=40).pack(pady=10, fill="x", padx=30)
        
        ctk.CTkButton(left_frame, text="انتخاب GeoJSON", 
                     command=self.load_geojson, height=40).pack(pady=10, fill="x", padx=30)
        
        ctk.CTkButton(left_frame, text="انتخاب KML/KMZ", 
                     command=self.load_kml, height=40).pack(pady=10, fill="x", padx=30)
        
        ctk.CTkButton(left_frame, text="انتخاب CSV با مختصات", 
                     command=self.load_csv, height=40).pack(pady=10, fill="x", padx=30)

        # نمایش اطلاعات لایه
        info_frame = ctk.CTkFrame(left_frame)
        info_frame.pack(fill="both", expand=True, pady=20, padx=20)

        ctk.CTkLabel(info_frame, text="اطلاعات لایه ورودی:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)

        self.input_info = ctk.CTkTextbox(info_frame, height=300)
        self.input_info.pack(fill="both", expand=True, padx=10, pady=10)

    def create_processing_tab(self):
        tab = self.tabview.tab("پردازش جغرافیایی")

        # فریم ابزارها
        tools_frame = ctk.CTkFrame(tab, width=300)
        tools_frame.pack(side="left", fill="y", padx=20, pady=20)
        tools_frame.pack_propagate(False)

        ctk.CTkLabel(tools_frame, text="🛠 ابزارهای پردازش", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        # بافر
        buffer_frame = ctk.CTkFrame(tools_frame)
        buffer_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(buffer_frame, text="بافر (متر):").pack(side="left", padx=10)
        self.buffer_entry = ctk.CTkEntry(buffer_frame, placeholder_text="مثلاً 1000")
        self.buffer_entry.pack(side="right", padx=10)
        ctk.CTkButton(tools_frame, text="ایجاد بافر", 
                     command=self.create_buffer).pack(pady=5, fill="x", padx=30)

        # سایر ابزارها
        ctk.CTkButton(tools_frame, text="محاسبه مساحت و محیط", 
                     command=self.calculate_area_perimeter).pack(pady=5, fill="x", padx=30)
        
        ctk.CTkButton(tools_frame, text="تقاطع (Intersection)", 
                     command=self.intersection).pack(pady=5, fill="x", padx=30)
        
        ctk.CTkButton(tools_frame, text="اتحاد (Union)", 
                     command=self.union).pack(pady=5, fill="x", padx=30)

        # نمایش نتیجه پردازش
        result_frame = ctk.CTkFrame(tab)
        result_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.process_info = ctk.CTkTextbox(result_frame, height=400)
        self.process_info.pack(fill="both", expand=True, padx=10, pady=10)

    def create_output_tab(self):
        tab = self.tabview.tab("خروجی و نمایش")

        # نقشه
        map_frame = ctk.CTkFrame(tab)
        map_frame.pack(fill="both", expand=True, padx=20, pady=(20, 10))

        ctk.CTkLabel(map_frame, text="🗺 نقشه تعاملی (Folium)", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        self.map_webview_btn = ctk.CTkButton(map_frame, text="نمایش نقشه در مرورگر", 
                                            command=self.show_map, height=50, font=ctk.CTkFont(size=14))
        self.map_webview_btn.pack(pady=20)

        # ذخیره خروجی
        save_frame = ctk.CTkFrame(tab)
        save_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(save_frame, text="ذخیره به عنوان Shapefile", 
                     command=self.save_shapefile).pack(side="left", padx=20, expand=True, fill="x")
        
        ctk.CTkButton(save_frame, text="ذخیره به عنوان GeoJSON", 
                     command=self.save_geojson).pack(side="right", padx=20, expand=True, fill="x")

    # توابع بارگذاری داده
    def load_shapefile(self):
        path = filedialog.askopenfilename(filetypes=[("Shapefile", "*.shp")])
        if path:
            self.load_data(path, "shp")

    def load_geojson(self):
        path = filedialog.askopenfilename(filetypes=[("GeoJSON", "*.geojson *.json")])
        if path:
            self.load_data(path, "geojson")

    def load_kml(self):
        path = filedialog.askopenfilename(filetypes=[("KML/KMZ", "*.kml *.kmz")])
        if path:
            self.load_data(path, "kml")

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if path:
            try:
                df = pd.read_csv(path)
                if 'lat' in df.columns and 'lon' in df.columns:
                    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")
                elif 'latitude' in df.columns and 'longitude' in df.columns:
                    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")
                else:
                    messagebox.showerror("خطا", "ستون‌های lat/lon پیدا نشد!")
                    return
                self.input_gdf = gdf
                self.show_input_info()
                messagebox.showinfo("موفق", f"{len(gdf)} نقطه بارگذاری شد")
            except Exception as e:
                messagebox.showerror("خطا", str(e))

    def load_data(self, path, format_type):
        try:
            if format_type == "kml":
                gdf = gpd.read_file(path, driver='KML')
            else:
                gdf = gpd.read_file(path)
            
            # تبدیل به WGS84 اگر نبود
            if gdf.crs is None:
                gdf.set_crs("EPSG:4326", inplace=True)
            else:
                gdf = gdf.to_crs("EPSG:4326")
                
            self.input_gdf = gdf
            self.show_input_info()
            messagebox.showinfo("موفق", f"لایه با {len(gdf)} عارضه بارگذاری شد")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بارگذاری: {str(e)}")

    def show_input_info(self):
        if self.input_gdf is None:
            self.input_info.delete("1.0", "end")
            self.input_info.insert("1.0", "هیچ داده‌ای بارگذاری نشده")
            return
            
        info = f"""
تعداد عارضه: {len(self.input_gdf)}
سیستم مختصات: {self.input_gdf.crs}
نوع هندسه: {self.input_gdf.geom_type.unique()}
ستون‌ها: {list(self.input_gdf.columns)}

نمونه داده‌ها:
{self.input_gdf.head(3).to_string()}
        """
        self.input_info.delete("1.0", "end")
        self.input_info.insert("1.0", info)

    # توابع پردازش
    def create_buffer(self):
        if self.input_gdf is None:
            messagebox.showwarning("هشدار", "ابتدا داده ورودی بارگذاری کنید")
            return
        try:
            distance = float(self.buffer_entry.get())
            if self.input_gdf.crs != "EPSG:32639":  # UTM برای ایران
                gdf_utm = self.input_gdf.to_crs("EPSG:32639")
            else:
                gdf_utm = self.input_gdf.copy()
                
            buffered = gdf_utm.buffer(distance)
            self.processed_gdf = gpd.GeoDataFrame(geometry=buffered, crs="EPSG:32639").to_crs("EPSG:4326")
            messagebox.showinfo("موفق", f"بافر {distance} متری ایجاد شد")
            self.show_process_result("بافر ایجاد شد")
        except:
            messagebox.showerror("خطا", "فاصله را درست وارد کنید")

    def calculate_area_perimeter(self):
        if self.input_gdf is None:
            return
        gdf = self.input_gdf.to_crs("EPSG:32639")
        gdf['مساحت_مترمربع'] = gdf.geometry.area
        gdf['محیط_متر'] = gdf.geometry.length
        gdf['مساحت_هکتار'] = gdf['مساحت_مترمربع'] / 10000
        self.processed_gdf = gdf.to_crs("EPSG:4326")
        self.show_process_result("مساحت و محیط محاسبه شد")

    def intersection(self):
        if self.input_gdf is None:
            return
        messagebox.showinfo("راهنما", "این ابزار برای تقاطع دو لایه است - در نسخه بعدی اضافه می‌شود")

    def union(self):
        if self.input_gdf is None:
            return
        if len(self.input_gdf) > 1:
            united = self.input_gdf.unary_union
            self.processed_gdf = gpd.GeoDataFrame(geometry=[united], crs=self.input_gdf.crs)
            self.show_process_result("اتحاد انجام شد")
        else:
            messagebox.showinfo("توجه", "برای اتحاد حداقل دو عارضه نیاز است")

    def show_process_result(self, message):
        self.process_info.delete("1.0", "end")
        self.process_info.insert("1.0", f"{message}\n\n")
        if self.processed_gdf is not None:
            self.process_info.insert("end", f"تعداد عارضه خروجی: {len(self.processed_gdf)}\n")
            self.process_info.insert("end", str(self.processed_gdf.head()))

    def show_map(self):
        data = self.processed_gdf if self.processed_gdf is not None else self.input_gdf
        if data is None or len(data) == 0:
            messagebox.showwarning("هشدار", "داده‌ای برای نمایش وجود ندارد")
            return

        # مرکز نقشه
        centroid = data.geometry.union_all().centroid
        m = folium.Map(location=[centroid.y, centroid.x], zoom_start=10, tiles="CartoDB positron")

        # اضافه کردن لایه
        folium.GeoJson(
            data.__geo_interface__,
            name="لایه پردازش شده",
            style_function=lambda x: {'fillColor': 'blue', 'color': 'black', 'weight': 2, 'fillOpacity': 0.5}
        ).add_to(m)

        # ابزارهای نقشه
        Draw(export=True).add_to(m)
        MeasureControl().add_to(m)
        folium.LayerControl().add_to(m)

        # ذخیره و نمایش
        map_path = os.path.join(os.getcwd(), "نقشه_آموزشی.html")
        m.save(map_path)
        webbrowser.open(f"file://{map_path}")

    def save_shapefile(self):
        if self.processed_gdf is None and self.input_gdf is None:
            messagebox.showwarning("هشدار", "داده‌ای برای ذخیره وجود ندارد")
            return
        path = filedialog.asksaveasfilename(defaultextension=".shp", filetypes=[("Shapefile", "*.shp")])
        if path:
            data = self.processed_gdf if self.processed_gdf is not None else self.input_gdf
            data.to_file(path, encoding='utf-8')
            messagebox.showinfo("موفق", "فایل با موفقیت ذخیره شد")

    def save_geojson(self):
        if self.processed_gdf is None and self.input_gdf is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".geojson", filetypes=[("GeoJSON", "*.geojson")])
        if path:
            data = self.processed_gdf if self.processed_gdf is not None else self.input_gdf
            data.to_file(path, driver="GeoJSON", encoding='utf-8')
            messagebox.showinfo("موفق", "فایل GeoJSON ذخیره شد")

# اجرای برنامه
if __name__ == "__main__":
    # نصب کتابخانه‌ها در صورت نیاز (یک بار)
    print("در حال نصب کتابخانه‌های مورد نیاز...")
    os.system("pip install customtkinter geopandas folium pandas openpyxl")

    app = EducationalGIS()
    app.mainloop()