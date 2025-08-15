def csv_stream(generator):
    for chunk in generator():
        yield chunk.encode('utf-8')
