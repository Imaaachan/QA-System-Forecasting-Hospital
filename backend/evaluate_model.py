import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, GridSearchCV

print("1. Membaca data historis kunjungan...")
df = pd.read_csv("data_kunjungan.csv")
df['tanggal_masuk'] = pd.to_datetime(df['tanggal_masuk'])
daily_visits = df.groupby('tanggal_masuk').size().reset_index(name='jumlah_pasien')

print("2. Melakukan Advanced Feature Engineering...")
daily_visits['day_of_week'] = daily_visits['tanggal_masuk'].dt.dayofweek
daily_visits['month'] = daily_visits['tanggal_masuk'].dt.month

# Fitur penanda akhir pekan
daily_visits['is_weekend'] = daily_visits['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)

# Lag Features: Mengambil data jumlah pasien dari hari sebelumnya dan minggu lalu
daily_visits['pasien_kemarin'] = daily_visits['jumlah_pasien'].shift(1)
daily_visits['pasien_minggu_lalu'] = daily_visits['jumlah_pasien'].shift(7)

# Hapus baris kosong (NaN) yang terbentuk akibat fungsi shift()
daily_visits = daily_visits.dropna()

X = daily_visits[['day_of_week', 'month', 'is_weekend', 'pasien_kemarin', 'pasien_minggu_lalu']]
y = daily_visits['jumlah_pasien']

print("3. Membagi data (80% Train, 20% Test)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

print("4. Tuning Model dengan GridSearchCV (Mohon tunggu sebentar)...")
rf = RandomForestRegressor(random_state=42)

# Menentukan grid kombinasi parameter yang akan diuji
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [5, 10, 15, None],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2]
}

# Cross-validation dengan 3 fold
grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=3, n_jobs=-1, scoring='r2')
grid_search.fit(X_train, y_train)

best_model = grid_search.best_estimator_
print(f"   Parameter Terbaik ditemukan: {grid_search.best_params_}")

print("5. Menghitung Prediksi pada Data Uji...")
y_pred = best_model.predict(X_test)

# Menghitung Metrik Evaluasi
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print("\n=== HASIL EVALUASI MODEL SETELAH TUNING ===")
print(f"Mean Absolute Error (MAE)      : {mae:.2f} pasien")
print(f"Root Mean Squared Error (RMSE) : {rmse:.2f} pasien")
print(f"R-squared (R2 Score)           : {r2:.4f}")
print("===========================================")