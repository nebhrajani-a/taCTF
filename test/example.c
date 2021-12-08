#include <stdio.h>
#include <stdbool.h>
#include <string.h>

#define MAX_INPUT_LEN 100

bool insecure_string_compare(const void *a, const void *b, size_t length) {
  const char *ca = a, *cb = b;
  for (size_t i = 0; i < length; i++)
    if (ca[i] != cb[i])
      return false;
  return true;
}

int main(void)
{
  char flag[] = "sigpwny{flag}";
  char input[MAX_INPUT_LEN];
  fgets(input, MAX_INPUT_LEN, stdin);

  if ((strlen(input) - 1) != strlen(flag)) {
    return 0;
  }
  else {
    insecure_string_compare(flag, input, strlen(flag));
  }

  return 0;
}
