#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <stdlib.h>
#include <signal.h>

#define PATH_MAX        4096    /* # chars in a path name including nul */

char *pathpip;
int pid1,pid2;

void usage(char *error){
    fprintf(stderr,"%s",error);
    fprintf(stdout,"Usage: [pipe name] [exe1] / [exe2]\n");
    fprintf(stdout,"\t exe1: write on the pipe\n");
    fprintf(stdout,"\t exe2: read on the pipe\n");
    fprintf(stdout,"the pipe is deleted afterr the exceution\n");
    exit(EXIT_FAILURE);
}

void finish(int code){
    fprintf( stderr, "[mypipe] SIGTERM received [%d]\n", code );
    fprintf(stderr,"[mypipe] waiting\n");
    kill(pid2,SIGINT);
    waitpid(pid2,NULL,0);
    kill(pid1,SIGINT);
    waitpid(pid1,NULL,0);
    remove(pathpip);
    exit(EXIT_SUCCESS);
}

char *getpathpip(char* pip_name){
    int i=0,j,len = 0;
    char path[PATH_MAX],*eleFind = "Eirballoon",*path_end = "/build/bin/pip",*res;
    readlink("/proc/self/exe", path, PATH_MAX*sizeof(char));
    // printf("--------- %s \n",path);
    while (path[i]!='\0')
    {   
        j=0;
        while (path[i++]==eleFind[j++]){
        }
        if (eleFind[j-1]=='\0'){
            
            break;
        }         
            
    } 
    if(path[i-1]=='\0'){
        printf("error\n");
        exit(EXIT_FAILURE);
    }

    path[i-1] = '\0';
    len = strlen(path);

    res = calloc(len+strlen(path_end)+strlen(pip_name)+2,sizeof(char));
    strcpy(res,path);
    strcat(res,path_end);
    
    /* verifie si dossier Eirballoon/build/bin/pip
        et le cree dans le cas échéant*/
    struct stat st = {0};
    if (stat(res, &st) == -1) {
        printf("creation of pipe directory");
       mkdir(res, 0700);
    }

    strcat(res,"/");
    strcat(res,pip_name);
    // free(path);
    return res;    
}

int main(int argc, char *argv[])
{
    int pipefd =-1,i,ok = 0;
    char *exec1,*exec2,**argv1,**argv2,*pipe_name;
    
    if (argc <3)
        usage("ERROR: Argument <3\n");

    pipe_name = argv[1];
    exec1 = argv[2];
    argv1 = argv+2;

    for ( i = 3; i < argc; i++)
    {
        // printf("%s\n",argv[i]);
        if(strlen(argv[i])==1){
            // printf("%c\n", argv[i][0]);
            if(argv[i][0]=='/'){
                argv2 = argv+i+1;
                exec2 = *argv2;
                argv[i] = NULL;
                ok = 1;
                break;
            }
        }
    }
    if(ok == 0) usage("ERROR: / not found \n");


    pathpip = getpathpip(pipe_name);

    if(mkfifo(pathpip,0600)!=0)
    {
        perror("Error on pipe creation: ");
        fprintf(stderr,"Previous pipe has been removed\n");
        remove(pathpip);
        mkfifo(pathpip,0600);
    }   
    if ( (pid1 = fork())==0)
    {
        /* exe1 */
        printf("[mypipe] start: %s\n",exec1);
        execv(exec1,argv1);
        perror("EROOR exec1 :");
        exit(EXIT_FAILURE);
    }
    
    if ( (pid2 = fork())==0)
    {
        /* exe2 */
        printf("[mypipe] start: %s\n",exec2);
        execv(exec2,argv2);
        perror("EROOR exec2 :");
        exit(EXIT_FAILURE);
    }
    signal( SIGTERM, &finish );
    signal( SIGINT , &finish );
    // signal( SIGALRM, &finish );
    wait(NULL);
    wait(NULL);

    remove(pathpip);
    free(pathpip);
    return 0;
}
