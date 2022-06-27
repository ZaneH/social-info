class Mapping:
  @classmethod
  def aggregate_field_names(self, arr):
    total_names = []
    for i in arr:
      for key in i:
        if key not in total_names:
          total_names.append(key)
    return total_names