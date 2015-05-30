#include <stdio.h>

void preprocess(char *array, int len,int *proc) {
	int k = 1,i;
	proc[0] = 0;
	for(i = 1; i<len; ++i)	{
		k = proc[k-1];
		if(array[k] == array[i]) {
			++k;
			proc[i] = k;
		}
	}
}
void KMP(char *word, char *string, int word_len) {
	int proc[word_len];
	preprocess(word,word_len,proc);
	int i;
	int q = 0;
	for(i = 0 ; string[i]!='\0'; ++i ) {
		if(word[q] != string[i] && q>0)	q = proc[q-1];
		if(q == word_len-1)	{
			printf("%d\n", i -	word_len + 1);
			q = proc[q-1];
		}
		if(word[q] == string[i])	++q;
	}
}

int main(){
	char array[] = "ASAGJGJGASAJBKKASALKASA";
	char word[] = "ASA";
	KMP(word,array,3); 
	return 0;

}