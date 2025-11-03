# from django.http import JsonResponse
# import pandas as pd
# import numpy as np
# from tensorflow.keras.models import load_model
# import matplotlib.pyplot as plt
# import yfinance as yf
# from datetime import datetime

# def getPredictPrice(request):
#     # try:
#     #     import keras
#     #     print("Keras is available.")
#     # except ImportError:
#     #     print("Keras is not available.")

#     # try:
#     #     import tensorflow as tf
#     #     print("TensorFlow is available.")
#     # except ImportError:
#     #     print("TensorFlow is not available.")


#     # Define start and end dates for fetching data
#     end = datetime.now()
#     start = datetime(end.year - 20, end.month, end.day)
    
#     # Download stock data using yfinance
#     stock = "GOOG"
#     google_data = yf.download(stock, start, end)
    
#     # Load the trained Keras model
#     # model = load_model("Latest_stock_price_model.keras")
    
#     # Calculate splitting length for train-test split
#     splitting_len = int(len(google_data) * 0.7)
    
#     # Prepare test data for prediction
#     x_test = pd.DataFrame(google_data.Close[splitting_len:])
    
#     # Calculate the moving average for 250 days
#     google_data['MA_for_250_days'] = google_data.Close.rolling(250).mean()
    
#     # Plot the graph
#     fig = plot_graph((15, 16), google_data['MA_for_250_days'], google_data)
    
#     # Convert the plot to a response
#     response = fig_to_response(fig)
    
#     return response

# def plot_graph(figsize, values, full_data):
#     fig = plt.figure(figsize=figsize)
#     plt.plot(values, "Orange")
#     plt.plot(full_data.Close, 'b')
#     return fig

# def fig_to_response(fig):
#     # Convert Matplotlib figure to a PNG image
#     import io
#     buf = io.BytesIO()
#     fig.savefig(buf, format='png')
#     buf.seek(0)
    
#     # Encode PNG image as base64 string
#     import base64
#     image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    
#     # Generate JSON response with base64-encoded image
#     response = JsonResponse({'image': image_base64})
#     return response
