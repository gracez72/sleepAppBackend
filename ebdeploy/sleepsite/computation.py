from scipy.signal import find_peaks
import numpy as np
from django.db.models import Count, Min, Max, Avg, Sum


def get_peaks(data, threshold):
    """ 
    Given array of sleep data return number of local maxima over given height 
    """
    peaks, _ = find_peaks(data, height=threshold)
    return peaks

def get_polyfit(data):
    """ 
    Given array of sleep data perform linear degression for 1, 2, 3, 4, 5 degree function and 
    return coefficients and degree of least error
    """
    fit_error = list()
    result_coeff = list()

    if (len(data) < 3):
        return result_coeff, 0
    
    x_val = list(range(len(data)))

    ## Compute errors and grab coefficients for functions up to degree 5
    for i in range(3):
        result = np.polyfit(x_val, data, i+1, full=True)
        result_coeff.append(result[0])                       # resulting coefficients
        if len(result[1]) > 0:                           # check error calculated
            fit_error.append(abs(result[1][0]))

            if (abs(result[1][0]) < 5):                  # prevent overfitting
                break 
        else:
            fit_error.append(np.finfo(np.float64).max)

    # Find index of min element
    min_index = np.argmin(fit_error)
    ret_coeff = result_coeff[min_index]

    # convert back to native python type
    ret_coeff = list(map(lambda x : x.item(), ret_coeff))
    degree = len(ret_coeff) - 1

    return ret_coeff, degree


def bin(data, bin_list):
    """ 
    Performs binning using given bin range.
    """
    bin_counts = np.histogram(data, bins=bin_list)
    result = list(map(lambda x : x.item() , bin_counts[0]))

    return result


def getSummary(queryset):
    """
    Computes averages, max, min for given queryset
    """
    average_hr = queryset.aggregate(Avg('heart_rate'))
    max_hr = queryset.aggregate(Max('heart_rate'))
    min_hr = queryset.aggregate(Min('heart_rate'))

    average_ol = queryset.aggregate(Avg('oxygen_level'))
    max_ol = queryset.aggregate(Max('oxygen_level'))
    min_ol = queryset.aggregate(Min('oxygen_level'))

    return average_hr, max_hr, min_hr, average_ol, max_ol, min_ol

def getStats(queryset):  
    """
    Computes amount of hours for given queryset and returns percentages below threshold of 60
    """
    if queryset is not None: 
        max_date = queryset.aggregate(Max('date'))["date__max"]
        min_date = queryset.aggregate(Min('date'))["date__min"]
        delta = 0
        total_time = 0
        if None not in (max_date, min_date):
            delta = max_date - min_date
            total_time = delta.total_seconds() / 3600

        total_count = queryset.aggregate(Count('id'))['id__count']
        if (total_count <= 0):
            awake_percentage = 0
            below_threshold = 0
            above_threshold = 0
            between_threshold = 0
        else:
            awake_percentage = queryset.filter(heart_rate__gte = 60).aggregate(Count('id'))['id__count'] / total_count * 100
            below_threshold = queryset.filter(heart_rate__lt = 40).aggregate(Count('id'))['id__count'] / total_count 
            above_threshold = queryset.filter(heart_rate__gt = 60).aggregate(Count('id'))['id__count'] / total_count
            between_threshold = queryset.filter(heart_rate__gte = 40, heart_rate__lte = 60).aggregate(Count('id'))['id__count'] / total_count

        return max_date, min_date, total_time, total_count, awake_percentage, below_threshold, above_threshold, between_threshold

    return None


def getBins(queryset):
    """
    Produces bin counts for given queryset for display as bar graph
    """
    data = list(queryset.values_list('heart_rate', flat=True))
    ol_data = list(queryset.values_list('oxygen_level', flat=True))

    # Heart rate binning: 
    hr_bins_list = list(range(20, 95, 5))
    ol_bins_list = list(range(50, 105, 5))

    hr_bin_count = bin(data, hr_bins_list)
    ol_bin_count = bin(ol_data, ol_bins_list)

    return hr_bins_list, ol_bins_list, hr_bin_count, ol_bin_count


def getPeaks(queryset):
    """
    Computes the number of local maxima and the ids of the sleepdata objects given queryset data
    """
    data = list(queryset.values_list('heart_rate', flat=True))
    id_index = list(queryset.values_list('id', flat=True))
    
    peaks = list(map(lambda x : x.item() , get_peaks(data, 50)))
    num_peaks = len(peaks)
    sleepdata_index = list(map(lambda x : id_index[x], peaks))
    sleepdata_peaks = list(map(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"), list(queryset.filter(pk__in=sleepdata_index).values_list('date', flat=True))))

    # Compute polynomial func with regression
    coefficients, degree = get_polyfit(data)

    return id_index, peaks, num_peaks, sleepdata_index, sleepdata_peaks, degree, coefficients


def getFormattedBins(hr_bins_list, ol_bins_list, hr_bin_count, ol_bin_count):
    """
    Returns formatted JSON bins list for recharts
    """
    ol_bin = list()
    ol_bin = list(map(lambda x: {"oxygen_bin": x}, ol_bins_list))
    
    for i in range(len(ol_bin_count)):
        ol_bin[i]['oxygen_level'] = ol_bin_count[i]

    hr_bin = list()
    hr_bin = list(map(lambda x: {"heart_rate_bin": x}, hr_bins_list))
    
    for i in range(len(hr_bin_count)):
        hr_bin[i]['heart_rate'] = hr_bin_count[i]

    return ol_bin, hr_bin

def getFunctionPoints(coefficients, degree, length):
    """
    Computes function points for display in graph given function
    Returns empty list if no function given
    """
    
    results = list()
    if (len(coefficients) == 0 or length < 1):
       return results
       
    else: 
        x = list(range(length))
        results = list(map(lambda x: {"x": x}, x))

        if (degree == 1):
            for i in range(len(results)):
                results[i]['y'] = coefficients[1] + coefficients[0] * x[i]
        elif (degree == 2):
            for i in range(len(results)):
                results[i]['y'] = coefficients[2] + (x[i] * coefficients[1]) + (x[i] * x[i] * coefficients[0])
        elif (degree == 3):
            for i in range(len(results)):
                results[i]['y'] = coefficients[3] + (coefficients[2] * x[i]) + (x[i] * x[i] * coefficients[1]) + (x[i] * x[i] * x[i] * coefficients[0])   
        else: 
            return list()
    return results