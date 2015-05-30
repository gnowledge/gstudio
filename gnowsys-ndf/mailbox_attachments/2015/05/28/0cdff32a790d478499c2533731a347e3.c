#include<stdio.h>
int noc;
int compare(char a, char b)
{
    noc++;
    if(a==b)
        return 1;
    return 0;
}
int len(char str[])
{
    int i;
    for(i=0;str[i]!='\0';i++);
    return i;
}

int brute_force(char s[],char w[])
{
    noc=0;
    int o=0,i,j,ls,lw,f=0;
    ls=len(s);
    lw=len(w);
    for(i=0;i<=(ls-lw);i++)
    {
        f=0;
        for(j=0;j<lw;j++)
        {
            if(compare(s[i],w[j]))
            {

                f++;
                i++;
            }
            else
               break;
        }
        i=(i-f);
        if(f==lw)
            o++;
    } 
    return o;
}

int* prefix_func(char w[])
{   
    int m=len(w);
    int t[m],k=0,i,q;
    t[0]=0;
    for(q=1;q<m;q++)
    {
        while((k>0)&&(!compare(w[k],w[q])))
           k=t[k-1];
        if(w[k]==w[q])
            k++;
        t[q]=k;           
    }
    return t;
}

int kmp(char s[],char w[])
{
    noc=0;
    int ls=len(s),lw=len(w);
    int* t=prefix_func(w);
    int i,q=0,o=0;
    for(i=0;i<ls;i++)
    {
        while((q>0)&&(!compare(w[q],s[i])))
            q=t[q-1];
        if(w[q]==s[i])
            q++;
        if(q==lw)
        {
            o++;        
            q=t[q-1];
        }
    }
    return o;
}

void return_index(char s[],char w[],int ar[])
{
    noc=0;
    int ls=len(s),lw=len(w);
    int* t=prefix_func(w);
    int i,q=0,o=0,k=0;
    for(i=0;i<100;i++)
        ar[i]=0;
    for(i=0;i<ls;i++)
    {
        while((q>0)&&(!compare(w[q],s[i])))
            q=t[q-1];
        if(w[q]==s[i])
            q++;
        if(q==lw)
        {
            o++; 
            ar[k++]=(i-lw+1);       
            q=t[q-1];
        }
    }
}

int find_p_S_s(char str[],char p[],char s[])
{
    int pr[100];
    return_index(str,p,pr);
    int i,j,o=0,si,pi;
    int sr[100];
    return_index(str,s,sr);
    printf("%d",*sr);
    
        printf("\n\n\n\n");
    for(i=0;i<(len(str)-len(p));i++)
        printf("%d\t",*(pr+i));
    printf("\n\n\n\n");
    for(i=0;i<(len(str)-len(s));i++)
        printf("%d\t",*(sr+i));


    for(i=1;i<100;i++)
        if(sr[i]==0)
            break;
    si=i;
    for(i=1;i<100;i++)
        if(pr[i]==0)
            break;
    pi=i;
    
    printf("\n%d,%d\n",si,pi);
    
    for(i=0;i<si;i++)
    {   for(j=0;j<pi;j++)
        {
            if(sr[i]>=(pr[j]+len(s)))
                o++;
        }
    }
    return o;
}

int main()
{
    char lstr[10000], sstr[100],p[100],s[100];
    scanf("%s%s",lstr,sstr);
    int bfa=brute_force(lstr,sstr);
    printf("brute force algo : %d , noc: %d\n",bfa,noc);
    int kmpr=kmp(lstr,sstr);
    printf("kmp algo result: %d,noc= %d\n",kmpr,noc);
    printf("enter p,s");
    scanf("%s%s",p,s);
    int o=find_p_S_s(lstr,p,s);
    printf("occourances of p_S_s: %d\n",o);
    return 0;    
}
